from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(auth_admin.UserAdmin):
    """
    Configuração do Admin para o modelo de Usuário customizado.
    """
    # Campos exibidos na lista de usuários
    list_display = ('matricula', 'nome_completo', 'email', 'is_active', 'is_staff', 'is_superuser')
    # Campos usados para busca
    search_fields = ('matricula', 'nome_completo', 'email')
    # Campos usados para filtros
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    
    # Campos exibidos ao editar um usuário (substitui 'username' por 'matricula')
    fieldsets = (
        (None, {'fields': ('matricula', 'password')}),
        ('Informações Pessoais', {'fields': ('nome_completo', 'email', 'cpf')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login',)}),
    )
    
    # Campos exibidos ao criar um usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matricula', 'nome_completo', 'email', 'password'),
        }),
    )
    
    # Campo usado para ordenação
    ordering = ('matricula',)
    
    # Remove 'username' do form de edição, já que não o usamos
    filter_horizontal = ('groups', 'user_permissions',)

