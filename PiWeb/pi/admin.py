from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Configuração do admin para o modelo Usuario
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos a serem exibidos na lista de usuários
    list_display = ('cpf', 'first_name', 'last_name', 'email', 'telefone', 'is_active', 'is_staff', 'date_joined')
    # Campos de filtro lateral
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    # Campos de busca
    search_fields = ('cpf', 'first_name', 'last_name', 'email', 'telefone')
    # Ordenação padrão
    ordering = ('cpf',)
    # Campos organizados em seções no formulário de edição
    fieldsets = (
        (None, {'fields': ('cpf', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'telefone', 'endereco')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    # Campos para adicionar novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cpf', 'first_name', 'last_name', 'email', 'telefone', 'endereco', 'password1', 'password2'),
        }),
    )
    # Campos somente leitura
    readonly_fields = ('date_joined', 'last_login')
