from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import Group

# Importando Modelos
from apps.users.models import Usuario
from apps.plantao.models import ( # CORREÇÃO AQUI
    EquipePlantao, ItemInventario, ChecklistStatus, ChecklistDetalhe
)
from apps.ocorrencias.models import (
    Ocorrencia, Localizacao, MaterialUtilizado, ApoioOcorrencia
)
from apps.pacientes.models import (
    Paciente, PertencesPaciente, InformacaoClinica, DadosEspecificosPaciente
)
from apps.dashboard.models import RelatorioGerencial

# --- Serializers de Leitura Simples (Usados em Aninhamento) ---

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class UsuarioSerializer(serializers.ModelSerializer):
    """ Serializer para o modelo Usuario (apenas Leitura) """
    groups = GroupSerializer(many=True, read_only=True)
    # Tenta obter o 'nivel_acesso', mas não falha se não existir
    nivel_acesso = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'matricula', 'nome_completo', 'email', 'groups', 'nivel_acesso']

    def get_nivel_acesso(self, obj):
        if obj.is_gerencial:
            return 'Gerencial'
        if obj.is_assistencial:
            return 'Assistencial'
        return 'N/A'


class ItemInventarioSerializer(serializers.ModelSerializer):
    """ Serializer para Itens de Inventário """
    # Mostra o nome do grupo em vez do ID
    responsavel_grupo = serializers.StringRelatedField()
    
    class Meta:
        model = ItemInventario
        fields = ['id', 'nome_item', 'responsavel_grupo']

class LocalizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localizacao
        exclude = ['id', 'ocorrencia'] # Exclui campos redundantes

class PertencesPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PertencesPaciente
        exclude = ['id', 'paciente']

class InformacaoClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacaoClinica
        exclude = ['id', 'paciente']

class DadosEspecificosPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DadosEspecificosPaciente
        exclude = ['paciente'] # PK é o paciente

class MaterialUtilizadoSerializer(serializers.ModelSerializer):
    item = serializers.StringRelatedField(read_only=True)
    usuario = serializers.StringRelatedField(read_only=True)
    
    # Campos 'write_only' para receber IDs ao criar/atualizar
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemInventario.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = MaterialUtilizado
        fields = ['id', 'item', 'quantidade_usada', 'usuario', 'item_id']
        read_only_fields = ('usuario',) # Usuário é definido automaticamente pela view


class ApoioOcorrenciaSerializer(serializers.ModelSerializer):
    equipe_apoio_id = serializers.PrimaryKeyRelatedField(
        queryset=EquipePlantao.objects.all(), source='equipe_apoio'
    )
    equipe_apoio = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ApoioOcorrencia
        fields = ['id', 'vtr_apoio_sigla', 'data_hora_apoio', 'equipe_apoio', 'equipe_apoio_id']

# --- Serializers de Leitura Aninhados (Read-Only) ---

class ChecklistDetalheSerializer(serializers.ModelSerializer):
    item = ItemInventarioSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemInventario.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = ChecklistDetalhe
        fields = ['id', 'item', 'item_id', 'quantidade', 'status_alerta']

class ChecklistStatusSerializer(serializers.ModelSerializer):
    equipe = serializers.StringRelatedField(read_only=True)
    usuario = serializers.StringRelatedField(read_only=True)
    detalhes = ChecklistDetalheSerializer(many=True) # Permite escrita aninhada

    equipe_id = serializers.PrimaryKeyRelatedField(
        queryset=EquipePlantao.objects.all(), source='equipe', write_only=True
    )

    class Meta:
        model = ChecklistStatus
        fields = [
            'id', 'equipe', 'equipe_id', 'usuario', 'data_hora', 
            'vtr_observacao', 'foto_vtr', 'detalhes'
        ]
        read_only_fields = ('usuario',) # Definido automaticamente pela view

    def create(self, validated_data):
        detalhes_data = validated_data.pop('detalhes', [])
        checklist = ChecklistStatus.objects.create(**validated_data)
        for detalhe_data in detalhes_data:
            ChecklistDetalhe.objects.create(checklist=checklist, **detalhe_data)
        return checklist

    def update(self, instance, validated_data):
        detalhes_data = validated_data.pop('detalhes', None)
        
        # Atualiza os campos do ChecklistStatus
        instance.equipe = validated_data.get('equipe', instance.equipe)
        instance.vtr_observacao = validated_data.get('vtr_observacao', instance.vtr_observacao)
        instance.foto_vtr = validated_data.get('foto_vtr', instance.foto_vtr)
        instance.save()

        # Atualiza/Cria/Deleta detalhes
        if detalhes_data is not None:
            # (Lógica mais complexa de atualização de itens aninhados seria necessária aqui)
            # Por simplicidade, vamos deletar os antigos e criar os novos
            instance.detalhes.all().delete()
            for detalhe_data in detalhes_data:
                ChecklistDetalhe.objects.create(checklist=instance, **detalhe_data)

        return instance


class PacienteReadSerializer(serializers.ModelSerializer):
    """ Serializer de LEITURA (GET) para Paciente (mostra tudo aninhado) """
    pertences = PertencesPacienteSerializer(read_only=True)
    info_clinica = InformacaoClinicaSerializer(read_only=True)
    dados_especificos = DadosEspecificosPacienteSerializer(read_only=True)
    
    class Meta:
        model = Paciente
        fields = [
            'id', 'ocorrencia', 'nome', 'idade', 'sexo', 'is_gestante', 
            'is_psiquiatrico', 'is_paliativo', 'recusa_atendimento', 
            'foto_recusa', 'pertences', 'info_clinica', 'dados_especificos'
        ]

class OcorrenciaReadSerializer(serializers.ModelSerializer):
    """ Serializer de LEITURA (GET) para Ocorrência (mostra tudo aninhado) """
    equipe = serializers.StringRelatedField()
    localizacao = LocalizacaoSerializer(read_only=True)
    pacientes = PacienteReadSerializer(many=True, read_only=True)
    materiais_utilizados = MaterialUtilizadoSerializer(many=True, read_only=True)
    viaturas_apoio = ApoioOcorrenciaSerializer(many=True, read_only=True)

    class Meta:
        model = Ocorrencia
        fields = [
            'id', 'num_reg_central', 'data_hora_inicio', 'tipo_ocorrencia', 
            'status_final', 'data_hora_finalizacao', 'finalizada', 
            'observacoes_audio', 'equipe', 'localizacao', 'pacientes', 
            'materiais_utilizados', 'viaturas_apoio'
        ]

# --- Serializers de Escrita (Write-Only/Read-Write) ---

class PacienteWriteSerializer(serializers.ModelSerializer):
    """ Serializer de ESCRITA (POST/PUT) para Paciente """
    pertences = PertencesPacienteSerializer(required=False)
    info_clinica = InformacaoClinicaSerializer(required=False)
    dados_especificos = DadosEspecificosPacienteSerializer(required=False)

    class Meta:
        model = Paciente
        fields = [
            'id', 'ocorrencia', 'nome', 'idade', 'sexo', 'is_gestante', 
            'is_psiquiatrico', 'is_paliativo', 'recusa_atendimento', 
            'foto_recusa', 'pertences', 'info_clinica', 'dados_especificos'
        ]

    def _create_or_update_nested(self, paciente, data, model_class, field_name):
        """Helper para criar/atualizar dados OneToOne aninhados."""
        nested_data = data.pop(field_name, None)
        if nested_data:
            # Tenta pegar o objeto existente; se não existir, cria um novo
            nested_instance, created = model_class.objects.update_or_create(
                paciente=paciente, defaults=nested_data
            )
            return nested_instance
        return None

    def create(self, validated_data):
        pertences_data = validated_data.pop('pertences', None)
        info_data = validated_data.pop('info_clinica', None)
        dados_data = validated_data.pop('dados_especificos', None)
        
        paciente = Paciente.objects.create(**validated_data)
        
        if pertences_data:
            PertencesPaciente.objects.create(paciente=paciente, **pertences_data)
        if info_data:
            InformacaoClinica.objects.create(paciente=paciente, **info_data)
        if dados_data:
            DadosEspecificosPaciente.objects.create(paciente=paciente, **dados_data)
            
        return paciente

    def update(self, instance, validated_data):
        # Atualiza os campos OneToOne
        self._create_or_update_nested(instance, validated_data, PertencesPaciente, 'pertences')
        self._create_or_update_nested(instance, validated_data, InformacaoClinica, 'info_clinica')
        self._create_or_update_nested(instance, validated_data, DadosEspecificosPaciente, 'dados_especificos')
        
        # Atualiza os campos do paciente
        return super().update(instance, validated_data)

class OcorrenciaWriteSerializer(serializers.ModelSerializer):
    """ Serializer de ESCRITA (POST/PUT) para Ocorrência """
    localizacao = LocalizacaoSerializer()
    pacientes = PacienteWriteSerializer(many=True, required=False)
    
    class Meta:
        model = Ocorrencia
        fields = [
            'id', 'equipe', 'num_reg_central', 'data_hora_inicio', 'tipo_ocorrencia',
            'status_final', 'data_hora_finalizacao', 'finalizada', 
            'observacoes_audio', 'localizacao', 'pacientes'
        ]
        validators = [
            # Validador de unicidade para 'num_reg_central'
            UniqueValidator(
                queryset=Ocorrencia.objects.all(),
                message="Já existe uma ocorrência com este Número de Registro Central."
            )
        ]

    def validate(self, data):
        """ Validação Nível de Objeto """
        if data.get('finalizada') == True:
            # Regra de Negócio: Se 'finalizada' for True, verifica campos
            if not data.get('status_final'):
                raise serializers.ValidationError("O 'Status Final' é obrigatório para finalizar a ficha.")
            if not data.get('data_hora_finalizacao'):
                raise serializers.ValidationError("A 'Data/Hora de Finalização' é obrigatória para finalizar a ficha.")
            
        return data

    def create(self, validated_data):
        localizacao_data = validated_data.pop('localizacao')
        pacientes_data = validated_data.pop('pacientes', [])
        
        ocorrencia = Ocorrencia.objects.create(**validated_data)
        
        # Cria a Localização associada
        Localizacao.objects.create(ocorrencia=ocorrencia, **localizacao_data)
        
        # Cria os Pacientes associados
        for paciente_data in pacientes_data:
            # (Remove dados aninhados do paciente para criar separadamente)
            pertences_data = paciente_data.pop('pertences', None)
            info_data = paciente_data.pop('info_clinica', None)
            dados_data = paciente_data.pop('dados_especificos', None)
            
            paciente = Paciente.objects.create(ocorrencia=ocorrencia, **paciente_data)
            
            if pertences_data:
                PertencesPaciente.objects.create(paciente=paciente, **pertences_data)
            if info_data:
                InformacaoClinica.objects.create(paciente=paciente, **info_data)
            if dados_data:
                DadosEspecificosPaciente.objects.create(paciente=paciente, **dados_data)
                
        return ocorrencia

    def update(self, instance, validated_data):
        localizacao_data = validated_data.pop('localizacao', None)
        pacientes_data = validated_data.pop('pacientes', None) # Lógica de update de pacientes é complexa

        # Atualiza a localização
        if localizacao_data:
            Localizacao.objects.update_or_create(
                ocorrencia=instance, defaults=localizacao_data
            )
        
        # (A lógica de atualização de pacientes aninhados é omitida por complexidade)
        # (Recomendado: Criar endpoints separados para /ocorrencias/<id>/pacientes/)
        
        return super().update(instance, validated_data)

# --- Serializers Padrão (Restantes) ---

class EquipePlantaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipePlantao
        fields = '__all__'

class RelatorioGerencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatorioGerencial
        fields = '__all__'

