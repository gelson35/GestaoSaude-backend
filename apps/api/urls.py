from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Cria um roteador padrão do DRF
router = DefaultRouter()

# Registra os ViewSets no roteador
# O 'basename' é obrigatório quando o ViewSet não tem um 'queryset' fixo
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'equipes', views.EquipePlantaoViewSet, basename='equipe')
router.register(r'itens-inventario', views.ItemInventarioViewSet, basename='item-inventario') # Correção aqui
router.register(r'checklists', views.ChecklistStatusViewSet, basename='checklist')
router.register(r'checklist-detalhes', views.ChecklistDetalheViewSet, basename='checklist-detalhe')
router.register(r'ocorrencias', views.OcorrenciaViewSet, basename='ocorrencia')
router.register(r'localizacoes', views.LocalizacaoViewSet, basename='localizacao')
router.register(r'materiais-utilizados', views.MaterialUtilizadoViewSet, basename='material-utilizado')
router.register(r'apoios-ocorrencia', views.ApoioOcorrenciaViewSet, basename='apoio-ocorrencia')
router.register(r'pacientes', views.PacienteViewSet, basename='paciente')
router.register(r'pertences', views.PertencesPacienteViewSet, basename='pertences')
router.register(r'info-clinicas', views.InformacaoClinicaViewSet, basename='info-clinica')
router.register(r'dados-especificos', views.DadosEspecificosPacienteViewSet, basename='dados-especificos')
router.register(r'relatorios', views.RelatorioGerencialViewSet, basename='relatorio')

# As URLs da API são determinadas automaticamente pelo roteador
urlpatterns = [
    path('', include(router.urls)),
]

