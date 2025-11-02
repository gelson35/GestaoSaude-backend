from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL da nossa API (v1)
    # Inclui o arquivo apps/api/urls.py
    path('', include('apps.api.urls')),
    
    # URLs de Login/Logout da API Navegável (Browsable API)
    path('api-auth/', include('rest_framework.urls')),
]

# Adiciona URLs de Mídia apenas em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

