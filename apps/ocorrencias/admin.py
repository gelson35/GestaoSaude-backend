from django.contrib import admin
from .models import Ocorrencia, Localizacao, MaterialUtilizado, ApoioOcorrencia

class LocalizacaoInline(admin.StackedInline):
    model = Localizacao
    extra = 0

class MaterialUtilizadoInline(admin.TabularInline):
    model = MaterialUtilizado
    extra = 0
    autocomplete_fields = ('item', 'usuario')

class ApoioOcorrenciaInline(admin.TabularInline):
    model = ApoioOcorrencia
    fk_name = 'ocorrencia_mestre'
    extra = 0
    autocomplete_fields = ('equipe_apoio',)

@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('num_reg_central', 'equipe', 'data_hora_inicio', 'status_final', 'finalizada')
    list_filter = ('finalizada', 'status_final', 'data_hora_inicio', 'localizacao__bairro')
    search_fields = ('num_reg_central', 'equipe__vtr_sigla', 'localizacao__bairro')
    inlines = [LocalizacaoInline, MaterialUtilizadoInline, ApoioOcorrenciaInline]
    autocomplete_fields = ('equipe',)

