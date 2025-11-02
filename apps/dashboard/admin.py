from django.contrib import admin
from .models import RelatorioGerencial

@admin.register(RelatorioGerencial)
class RelatorioGerencialAdmin(admin.ModelAdmin):
    list_display = ('tipo_relatorio', 'data_referencia', 'data_geracao', 'total_ocorrencias')
    list_filter = ('tipo_relatorio', 'data_referencia')

