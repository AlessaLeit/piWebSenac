from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class CPFBackend(ModelBackend):
    """
    Autentica um usuário usando apenas CPF.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta encontrar um usuário que corresponda ao CPF
            user = Usuario.objects.get(cpf=username)
        except Usuario.DoesNotExist:
            return None

        # Se o usuário foi encontrado, verifica a senha
        if user.check_password(password):
            return user
        return None
