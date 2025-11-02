from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
)
from django.utils.translation import gettext_lazy as _

class UsuarioManager(BaseUserManager):
    """
    Manager para o nosso modelo de usuário customizado.
    """
    def create_user(self, matricula, nome_completo, email, password=None, **extra_fields):
        """
        Cria e salva um usuário comum com matrícula, e-mail e senha.
        """
        if not matricula:
            raise ValueError('O usuário deve ter uma matrícula')
        if not email:
            raise ValueError('O usuário deve ter um e-mail')
        
        email = self.normalize_email(email)
        user = self.model(
            matricula=matricula,
            nome_completo=nome_completo,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricula, nome_completo, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        return self.create_user(
            matricula=matricula,
            nome_completo=nome_completo,
            email=email,
            password=password,
            **extra_fields
        )

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuário customizado (Tabela: USUARIOS)
    Função e Nível de Acesso são controlados por Grupos.
    """
    matricula = models.CharField(max_length=6, unique=True, verbose_name='Matrícula')
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    nome_completo = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_staff = models.BooleanField(default=False) # Permite acesso ao /admin

    objects = UsuarioManager()

    # Define o campo de login
    USERNAME_FIELD = 'matricula'
    
    # Campos requeridos ao criar um superuser
    REQUIRED_FIELDS = ['nome_completo', 'email']

    # --- CORREÇÃO PARA O ERRO E304 ---
    # Precisamos adicionar 'related_name' para evitar conflito
    # com o modelo auth.User padrão do Django.
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        # Nome reverso único para o nosso modelo Usuario
        related_name="usuario_set", 
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        # Nome reverso único para o nosso modelo Usuario
        related_name="usuario_permission_set", 
        related_query_name="usuario",
    )
    # --- FIM DA CORREÇÃO ---

    def __str__(self):
        return f"{self.nome_completo} ({self.matricula})"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'users_usuario' # Prefixo do app + nome do modelo

    # --- Propriedades de Permissão Baseadas em Grupo ---
    
    @property
    def is_gerencial(self):
        """Verifica se o usuário pertence a um grupo gerencial."""
        # 'is_superuser' tem acesso total
        if self.is_superuser:
            return True
        # Verifica se o usuário está no grupo 'Administração'
        return self.groups.filter(name='Administração').exists()

    @property
    def is_assistencial(self):
        """Verifica se o usuário pertence a um grupo assistencial."""
        grupos_assistenciais = [
            'Médico', 'Enfermeiro', 'Técnico de Enfermagem', 'Condutor'
        ]
        return self.groups.filter(name__in=grupos_assistenciais).exists()

