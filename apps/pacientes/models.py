from django.db import models

# Tabela: PACIENTES
class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('I', 'Não Informado'),
    ]
    
    ocorrencia = models.ForeignKey('ocorrencias.Ocorrencia', on_delete=models.CASCADE, related_name='pacientes')
    nome = models.CharField(max_length=100)
    idade = models.PositiveIntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    is_gestante = models.BooleanField(default=False)
    is_psiquiatrico = models.BooleanField(default=False)
    is_paliativo = models.BooleanField(default=False)
    recusa_atendimento = models.BooleanField(default=False)
    foto_recusa = models.ImageField(upload_to='fotos_recusa/', null=True, blank=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        db_table = 'pacientes_paciente'

# Tabela: PERTENCES_PACIENTE
class PertencesPaciente(models.Model):
    paciente = models.OneToOneField('pacientes.Paciente', on_delete=models.CASCADE, related_name='pertences')
    descricao_pertences = models.TextField(null=True, blank=True)
    valores_encontrados = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entregue_para = models.CharField(max_length=100, null=True, blank=True)
    foto_pertences = models.ImageField(upload_to='fotos_pertences/', null=True, blank=True)

    def __str__(self):
        return f"Pertences de {self.paciente.nome}"
    
    class Meta:
        verbose_name = 'Pertences do Paciente'
        verbose_name_plural = 'Pertences dos Pacientes'
        db_table = 'pacientes_pertences_paciente'

# Tabela: INFORMACAO_CLINICA
class InformacaoClinica(models.Model):
    paciente = models.OneToOneField('pacientes.Paciente', on_delete=models.CASCADE, related_name='info_clinica')
    gravidade_cor = models.CharField(max_length=20, null=True, blank=True)
    gravidade_texto = models.CharField(max_length=20, null=True, blank=True)
    pressao_arterial = models.CharField(max_length=10, null=True, blank=True)
    frequencia_cardiaca = models.PositiveIntegerField(null=True, blank=True)
    frequencia_respiratoria = models.CharField(max_length=20, null=True, blank=True)
    eva_dor = models.PositiveIntegerField(null=True, blank=True, verbose_name='Escala Visual de Dor (EVA)')
    glasgow_total = models.PositiveIntegerField(null=True, blank=True)
    cincinnati_status = models.CharField(max_length=50, null=True, blank=True)
    mallampati_classe = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Info Clínica de {self.paciente.nome}"

    class Meta:
        verbose_name = 'Informação Clínica'
        verbose_name_plural = 'Informações Clínicas'
        db_table = 'pacientes_informacao_clinica'

# Tabela: DADOS_ESPECIFICOS_PACIENTE
class DadosEspecificosPaciente(models.Model):
    # PK e FK, como no seu SQL
    paciente = models.OneToOneField('pacientes.Paciente', on_delete=models.CASCADE, primary_key=True, related_name='dados_especificos')
    
    # Campos Gestante
    idade_gestacional = models.CharField(max_length=50, null=True, blank=True)
    perdas = models.BooleanField(null=True, blank=True)
    sangramento = models.BooleanField(null=True, blank=True)
    cartao_pre_natal = models.BooleanField(null=True, blank=True)
    movimentos_fetais = models.BooleanField(null=True, blank=True)
    
    # Campos Psiquiátrico
    contato_responsavel = models.CharField(max_length=50, null=True, blank=True)
    faz_tratamento = models.BooleanField(null=True, blank=True)
    observacoes_psiquiatricas = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Dados Específicos de {self.paciente.nome}"

    class Meta:
        verbose_name = 'Dado Específico do Paciente'
        verbose_name_plural = 'Dados Específicos dos Pacientes'
        db_table = 'pacientes_dados_especificos_paciente'

