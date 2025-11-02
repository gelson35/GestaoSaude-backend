from django.contrib import admin
from .models import Paciente, PertencesPaciente, InformacaoClinica, DadosEspecificosPaciente

class PertencesPacienteInline(admin.StackedInline):
    model = PertencesPaciente
    extra = 0

class InformacaoClinicaInline(admin.StackedInline):
    model = InformacaoClinica
    extra = 0

class DadosEspecificosPacienteInline(admin.StackedInline):
    model = DadosEspecificosPaciente
    extra = 0

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ocorrencia', 'idade', 'sexo', 'recusa_atendimento')
    list_filter = ('sexo', 'is_gestante', 'is_psiquiatrico', 'is_paliativo', 'recusa_atendimento')
    search_fields = ('nome', 'ocorrencia__num_reg_central')
    inlines = [InformacaoClinicaInline, DadosEspecificosPacienteInline, PertencesPacienteInline]
    autocomplete_fields = ('ocorrencia',)

