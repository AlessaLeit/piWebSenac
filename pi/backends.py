from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class CPFBackend(ModelBackend):
    """
    Autentica um usuário usando apenas CPF.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Limpar CPF para autenticação (remover pontos e traço)
            cpf_limpo = ''.join(filter(str.isdigit, username))
            # Tenta encontrar um usuário que corresponda ao CPF limpo
            user = Usuario.objects.get(cpf=cpf_limpo)
        except Usuario.DoesNotExist:
            return None

        # Se o usuário foi encontrado, verifica a senha
        if user.check_password(password):
            return user
        return None
