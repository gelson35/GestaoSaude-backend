from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import Group

# Importando Modelos
from apps.users.models import Usuario
from apps.plantao.models import (
    EquipePlantao, ItemInventario, ChecklistStatus, ChecklistDetalhe
)
from apps.ocorrencias.models import (
    Ocorrencia, Localizacao, MaterialUtilizado, ApoioOcorrencia
)
from apps.pacientes.models import (
    Paciente, PertencesPaciente, InformacaoClinica, DadosEspecificosPaciente
)
from apps.dashboard.models import RelatorioGerencial

# Importando Serializers
from . import serializers

# Importando Permissões Customizadas
from .permissions import IsAdminOrGerencial, IsAssistencialSafe, IsOwnerOrGerencial

# --- ViewSets ---

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para listar Usuários (apenas leitura).
    Apenas Gerencial/Admin podem ver.
    """
    queryset = Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [IsAdminOrGerencial] # Apenas Gerencial/Admin

class EquipePlantaoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Equipes de Plantão.
    Assistencial pode criar/ler. Gerencial pode tudo.
    """
    queryset = EquipePlantao.objects.all()
    serializer_class = serializers.EquipePlantaoSerializer
    permission_classes = [IsAssistencialSafe] # Assistencial pode criar/ler

class ItemInventarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Itens de Inventário.
    - Filtra itens pelo grupo do usuário (ex: Médico só vê itens de Médico).
    - Apenas Gerencial/Admin podem criar/editar/deletar itens.
    """
    serializer_class = serializers.ItemInventarioSerializer
    permission_classes = [IsAdminOrGerencial] # Apenas Gerencial/Admin gerencia itens

    def get_queryset(self):
        """
        Filtra os itens baseado no grupo do usuário.
        """
        user = self.request.user
        if not user.is_authenticated:
            return ItemInventario.objects.none()

        # Gerencial/Admin vê todos os itens
        # --- CORREÇÃO AQUI ---
        if user.is_gerencial:
            return ItemInventario.objects.all()
        
        # Assistencial vê itens "sem grupo" OU itens do(s) seu(s) grupo(s)
        # --- CORREÇÃO AQUI ---
        if user.is_assistencial:
            user_groups = user.groups.all()
            return ItemInventario.objects.filter(
                Q(responsavel_grupo__isnull=True) |
                Q(responsavel_grupo__in=user_groups)
            )
        
        return ItemInventario.objects.none()

class ChecklistStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint para o Checklist (Cabeçalho).
    - Assistencial pode criar/ler/editar OS SEUS PRÓPRIOS checklists.
    - Gerencial pode ler/editar TODOS.
    """
    queryset = ChecklistStatus.objects.all()
    # Usa permissão de "Dono"
    permission_classes = [IsOwnerOrGerencial]

    def get_serializer_class(self):
        """
        Usa um serializer simples para Escrita (POST/PUT) e um
        complexo para Leitura (GET).
        """
        if self.action in ['list', 'retrieve']:
            return serializers.ChecklistStatusSerializer
        
        # Para POST/PUT/PATCH (Ação de escrita)
        # (Idealmente, criaríamos um WriteSerializer simples)
        return serializers.ChecklistStatusSerializer

    def get_queryset(self):
        """
        Filtra para que Assistencial veja apenas seus checklists.
        """
        user = self.request.user
        if not user.is_authenticated:
            return ChecklistStatus.objects.none()
        
        # --- CORREÇÃO AQUI ---
        if user.is_gerencial:
            return ChecklistStatus.objects.all() # Gerencial vê tudo
        
        # Assistencial vê apenas os checklists que ele assinou
        return ChecklistStatus.objects.filter(usuario=user)

    def perform_create(self, serializer):
        """
        Associa automaticamente o usuário logado ao criar um checklist.
        """
        serializer.save(usuario=self.request.user)

class ChecklistDetalheViewSet(viewsets.ModelViewSet):
    """
    API endpoint para os Itens (Detalhes) de um Checklist.
    (Permissão é herdada do 'pai', o ChecklistStatus)
    """
    queryset = ChecklistDetalhe.objects.all()
    serializer_class = serializers.ChecklistDetalheSerializer
    permission_classes = [IsOwnerOrGerencial] # Mesma permissão do 'pai'
    
    def get_queryset(self):
        """
        Filtra para que Assistencial veja apenas detalhes
        dos seus checklists.
        """
        user = self.request.user
        if not user.is_authenticated:
            return ChecklistDetalhe.objects.none()
        
        # --- CORREÇÃO AQUI ---
        if user.is_gerencial:
            return ChecklistDetalhe.objects.all() # Gerencial vê tudo
        
        # Assistencial vê apenas detalhes de checklists que ele assinou
        return ChecklistDetalhe.objects.filter(checklist__usuario=user)

class OcorrenciaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Ocorrências.
    Usa serializers diferentes para Leitura e Escrita.
    """
    queryset = Ocorrencia.objects.all()
    permission_classes = [IsAssistencialSafe] # Assistencial pode criar/ler

    def get_serializer_class(self):
        """
        Escolhe o serializer baseado na ação:
        - GET: Usa OcorrenciaReadSerializer (mostra tudo aninhado)
        - POST/PUT/PATCH: Usa OcorrenciaWriteSerializer (valida e salva)
        """
        if self.action in ['list', 'retrieve']:
            return serializers.OcorrenciaReadSerializer
        return serializers.OcorrenciaWriteSerializer

    def get_queryset(self):
        """
        (Opcional) Poderíamos filtrar ocorrências por equipe do usuário,
        mas por enquanto, todos assistenciais veem todas.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Ocorrencia.objects.none()
        
        return Ocorrencia.objects.all()

class LocalizacaoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Localização.
    (Permissão herdada da Ocorrência)
    """
    queryset = Localizacao.objects.all()
    serializer_class = serializers.LocalizacaoSerializer
    permission_classes = [IsAssistencialSafe]

class MaterialUtilizadoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Materiais Utilizados.
    """
    queryset = MaterialUtilizado.objects.all()
    serializer_class = serializers.MaterialUtilizadoSerializer
    permission_classes = [IsAssistencialSafe]

    def perform_create(self, serializer):
        """
        Associa automaticamente o usuário logado ao registrar um material.
        """
        serializer.save(usuario=self.request.user)
        
    def get_queryset(self):
        """
        Filtra para que Gerencial veja tudo, e Assistencial
        veja apenas os materiais que ele registrou.
        """
        user = self.request.user
        if not user.is_authenticated:
            return MaterialUtilizado.objects.none()
        
        # --- CORREÇÃO AQUI ---
        if user.is_gerencial:
            return MaterialUtilizado.objects.all() # Gerencial vê tudo
        
        # Assistencial vê apenas os que ele registrou
        return MaterialUtilizado.objects.filter(usuario=user)

class ApoioOcorrenciaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Viaturas de Apoio.
    """
    queryset = ApoioOcorrencia.objects.all()
    serializer_class = serializers.ApoioOcorrenciaSerializer
    permission_classes = [IsAssistencialSafe]

class PacienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Pacientes.
    Usa serializers diferentes para Leitura e Escrita.
    """
    queryset = Paciente.objects.all()
    permission_classes = [IsAssistencialSafe]

    def get_serializer_class(self):
        """
        Escolhe o serializer baseado na ação:
        - GET: Usa PacienteReadSerializer (mostra tudo aninhado)
        - POST/PUT/PATCH: Usa PacienteWriteSerializer (valida e salva)
        """
        if self.action in ['list', 'retrieve']:
            return serializers.PacienteReadSerializer
        return serializers.PacienteWriteSerializer

class PertencesPacienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Pertences do Paciente.
    """
    queryset = PertencesPaciente.objects.all()
    serializer_class = serializers.PertencesPacienteSerializer
    permission_classes = [IsAssistencialSafe]

class InformacaoClinicaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Informações Clínicas.
    """
    queryset = InformacaoClinica.objects.all()
    serializer_class = serializers.InformacaoClinicaSerializer
    permission_classes = [IsAssistencialSafe]

class DadosEspecificosPacienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Dados Específicos do Paciente.
    """
    queryset = DadosEspecificosPaciente.objects.all()
    serializer_class = serializers.DadosEspecificosPacienteSerializer
    permission_classes = [IsAssistencialSafe]

# --- ViewSets Gerenciais ---
class RelatorioGerencialViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Relatórios Gerenciais.
    Apenas Gerencial/Admin podem acessar.
    """
    queryset = RelatorioGerencial.objects.all()
    serializer_class = serializers.RelatorioGerencialSerializer
    permission_classes = [IsAdminOrGerencial] # Apenas Gerencial/Admin

