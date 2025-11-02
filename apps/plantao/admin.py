from django.contrib import admin
from .models import EquipePlantao, ItemInventario, ChecklistStatus, ChecklistDetalhe

@admin.register(EquipePlantao)
class EquipePlantaoAdmin(admin.ModelAdmin):
    list_display = ('vtr_sigla', 'data_plantao', 'condutor', 'tecnico_enf', 'enfermeiro', 'medico')
    list_filter = ('data_plantao', 'vtr_sigla')
    search_fields = ('vtr_sigla', 'condutor__nome_completo', 'tecnico_enf__nome_completo')
    autocomplete_fields = ('condutor', 'tecnico_enf', 'enfermeiro', 'medico')

@admin.register(ItemInventario)
class ItemInventarioAdmin(admin.ModelAdmin):
    list_display = ('nome_item', 'responsavel_grupo')
    list_filter = ('responsavel_grupo',)
    search_fields = ('nome_item',)
    autocomplete_fields = ('responsavel_grupo',) # Facilita a seleção

class ChecklistDetalheInline(admin.TabularInline):
    model = ChecklistDetalhe
    extra = 0
    autocomplete_fields = ('item',)

@admin.register(ChecklistStatus)
class ChecklistStatusAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'usuario', 'data_hora')
    list_filter = ('data_hora', 'usuario')
    search_fields = ('equipe__vtr_sigla', 'usuario__nome_completo')
    inlines = [ChecklistDetalheInline]
    autocomplete_fields = ('equipe', 'usuario')
