from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group

# Tabela: EQUIPES_PLANTAO
class EquipePlantao(models.Model):
    vtr_sigla = models.CharField(max_length=20, verbose_name='Sigla VTR')
    data_plantao = models.DateField()
    condutor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='equipes_como_condutor'
    )
    tecnico_enf = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='equipes_como_tecnico'
    )
    enfermeiro = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='equipes_como_enfermeiro', 
        null=True, 
        blank=True
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='equipes_como_medico', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.vtr_sigla} - {self.data_plantao.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = 'Equipe de Plantão'
        verbose_name_plural = 'Equipes de Plantão'
        unique_together = ('vtr_sigla', 'data_plantao')
        db_table = 'plantao_equipe_plantao' # CORREÇÃO AQUI

# Tabela: INVENTARIO_ITENS
class ItemInventario(models.Model):
    nome_item = models.CharField(max_length=100, unique=True)
    
    # Alteração: Ligado diretamente ao Grupo do Django
    responsavel_grupo = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name='Grupo Responsável',
        help_text='Grupo responsável pelo checklist deste item (ex: Médico, Condutor)'
    )

    def __str__(self):
        return self.nome_item

    class Meta:
        verbose_name = 'Item de Inventário'
        verbose_name_plural = 'Itens de Inventário'
        db_table = 'plantao_item_inventario' # CORREÇÃO AQUI

# Tabela: CHECKLIST_STATUS
class ChecklistStatus(models.Model):
    equipe = models.ForeignKey('plantao.EquipePlantao', on_delete=models.CASCADE, related_name='checklists') # CORREÇÃO AQUI
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='checklists_assinados')
    data_hora = models.DateTimeField(auto_now_add=True)
    vtr_observacao = models.TextField(null=True, blank=True, verbose_name='Observações da VTR')
    foto_vtr = models.ImageField(upload_to='fotos_vtr/', null=True, blank=True, verbose_name='Foto de Avaria')

    def __str__(self):
        return f"Checklist {self.equipe} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Status do Checklist'
        verbose_name_plural = 'Status dos Checklists'
        db_table = 'plantao_checklist_status' # CORREÇÃO AQUI

# Tabela: CHECKLIST_DETALHES
class ChecklistDetalhe(models.Model):
    STATUS_ALERTA_CHOICES = [
        ('VERDE', 'Verde'),
        ('AMARELO', 'Amarelo'),
        ('VERMELHO', 'Vermelho'),
    ]
    
    checklist = models.ForeignKey('plantao.ChecklistStatus', on_delete=models.CASCADE, related_name='detalhes') # CORREÇÃO AQUI
    item = models.ForeignKey('plantao.ItemInventario', on_delete=models.PROTECT, related_name='itens_checklist') # CORREÇÃO AQUI
    quantidade = models.IntegerField()
    status_alerta = models.CharField(max_length=20, choices=STATUS_ALERTA_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.item.nome_item} (Qtd: {self.quantidade})"

    class Meta:
        unique_together = ('checklist', 'item')
        verbose_name = 'Detalhe do Checklist'
        verbose_name_plural = 'Detalhes do Checklist'
        db_table = 'plantao_checklist_detalhe' # CORREÇÃO AQUI
