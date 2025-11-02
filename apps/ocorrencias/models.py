from django.db import models
from django.conf import settings

# Tabela: OCORRENCIAS
# Garanta que o nome da classe é 'Ocorrencia' (com 'O' maiúsculo)
class Ocorrencia(models.Model):
    equipe = models.ForeignKey('plantao.EquipePlantao', on_delete=models.PROTECT, related_name='ocorrencias')
    num_reg_central = models.CharField(max_length=20, unique=True, verbose_name='Nº Registro Central')
    data_hora_inicio = models.DateTimeField()
    tipo_ocorrencia = models.TextField()
    status_final = models.CharField(max_length=50)
    data_hora_finalizacao = models.DateTimeField(null=True, blank=True)
    finalizada = models.BooleanField(default=False)
    observacoes_audio = models.FileField(upload_to='audios_ocorrencias/', null=True, blank=True)

    def __str__(self):
        return f"Ocorrência {self.num_reg_central}"

    class Meta:
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'
        db_table = 'ocorrencias_ocorrencia'

# Tabela: LOCALIZACAO
class Localizacao(models.Model):
    ocorrencia = models.OneToOneField('ocorrencias.Ocorrencia', on_delete=models.CASCADE, related_name='localizacao')
    endereco = models.TextField()
    bairro = models.CharField(max_length=50)
    foto_local = models.ImageField(upload_to='fotos_locais/', null=True, blank=True)
    meios_acionados = models.TextField(null=True, blank=True)
    info_transito = models.TextField(null=True, blank=True, verbose_name='Informações DPVAT')
    link_gps = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Localização da Ocorrência {self.ocorrencia.num_reg_central}"
    
    class Meta:
        verbose_name = 'Localização'
        verbose_name_plural = 'Localizações'
        db_table = 'ocorrencias_localizacao'

# Tabela: MATERIAIS_UTILIZADOS
class MaterialUtilizado(models.Model):
    ocorrencia = models.ForeignKey('ocorrencias.Ocorrencia', on_delete=models.CASCADE, related_name='materiais_utilizados')
    item = models.ForeignKey('plantao.ItemInventario', on_delete=models.PROTECT, related_name='usos_em_ocorrencias')
    quantidade_usada = models.PositiveIntegerField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='materiais_registrados')

    def __str__(self):
        return f"{self.quantidade_usada}x {self.item.nome_item} em {self.ocorrencia.num_reg_central}"

    class Meta:
        verbose_name = 'Material Utilizado'
        verbose_name_plural = 'Materiais Utilizados'
        db_table = 'ocorrencias_material_utilizado'

# Tabela: APOIO_OCORRENCIA
class ApoioOcorrencia(models.Model):
    ocorrencia_mestre = models.ForeignKey('ocorrencias.Ocorrencia', on_delete=models.CASCADE, related_name='viaturas_apoio')
    vtr_apoio_sigla = models.CharField(max_length=20, verbose_name='Sigla VTR Apoio')
    data_hora_apoio = models.DateTimeField()
    equipe_apoio = models.ForeignKey('plantao.EquipePlantao', on_delete=models.PROTECT, related_name='apoios_prestados')

    def __str__(self):
        return f"Apoio {self.vtr_apoio_sigla} para {self.ocorrencia_mestre.num_reg_central}"
    
    class Meta:
        verbose_name = 'Apoio de Ocorrência'
        verbose_name_plural = 'Apoios de Ocorrências'
        db_table = 'ocorrencias_apoio_ocorrencia'

