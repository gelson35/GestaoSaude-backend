from rest_framework import permissions

class IsAdminOrGerencial(permissions.BasePermission):
    """
    Permissão customizada para permitir acesso total apenas para
    usuários Gerenciais (Grupo 'Administração') ou Superusers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # --- CORREÇÃO AQUI ---
        # Acessa como propriedade (user.is_gerencial), não como método
        return request.user.is_gerencial

class IsAssistencialSafe(permissions.BasePermission):
    """
    Permissão para Nível Assistencial (Médico, Enfermeiro, etc.).
    - Permite Leitura (GET, HEAD, OPTIONS) para todos.
    - Permite Criação (POST) para Assistencial.
    - Permite Edição/Deleção (PUT, PATCH, DELETE) apenas para Gerencial.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Leitura é permitida para qualquer autenticado (Assistencial ou Gerencial)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # --- CORREÇÃO AQUI ---
        # (user.is_assistencial OU user.is_gerencial)
        # Permite POST para Assistencial e Gerencial
        if request.method == 'POST':
            return request.user.is_assistencial or request.user.is_gerencial

        # Permite PUT, PATCH, DELETE apenas para Gerencial
        # --- CORREÇÃO AQUI ---
        return request.user.is_gerencial

class IsOwnerOrGerencial(permissions.BasePermission):
    """
    Permissão para objetos que têm um dono (campo 'usuario').
    - Permite que o 'dono' (usuário Assistencial) edite/delete.
    - Permite que Gerencial edite/delete qualquer objeto.
    """
    
    def has_object_permission(self, request, view, obj):
        # Gerencial pode editar/deletar qualquer coisa
        # --- CORREÇÃO AQUI ---
        if request.user.is_gerencial:
            return True
        
        # Assistencial pode editar/deletar APENAS se for o dono
        # (obj.usuario é o dono do Checklist, request.user é quem faz a requisição)
        return obj.usuario == request.user

    def has_permission(self, request, view):
        # Qualquer usuário autenticado pode (tentar) listar ou criar
        return request.user and request.user.is_authenticated

