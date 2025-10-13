from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Para ter uma melhor experiência de administração com um modelo de usuário customizado,
# criamos uma classe de admin que herda de UserAdmin.
class CustomUserAdmin(UserAdmin):
    # Adiciona os campos customizados aos formulários de criação e edição no admin.
    # Mantemos os fieldsets padrão e adicionamos uma nova seção.
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('cpf', 'telefone', 'endereco')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        # O campo 'email' já está no add_fieldsets padrão, mas garantimos que os outros estejam aqui.
        ('Informações Adicionais', {'fields': ('cpf', 'telefone', 'endereco')}),
    )

    # Define quais colunas aparecerão na lista de usuários.
    list_display = ('username', 'email', 'first_name', 'cpf', 'is_staff')
    # Adiciona campos para busca.
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cpf')

# Registra o modelo 'Usuario' com a classe de admin customizada.
admin.site.register(Usuario, CustomUserAdmin)
