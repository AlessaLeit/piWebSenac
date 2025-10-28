from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import Usuario

class CPFOrEmailOrTelefoneBackend(ModelBackend):
    """
    Autentica um usuário usando CPF, email ou telefone.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta encontrar um usuário que corresponda ao cpf, email ou telefone
            user = Usuario.objects.get(
                Q(cpf=username) | Q(email=username) | Q(telefone=username)
            )
        except Usuario.DoesNotExist:
            return None

        # Se o usuário foi encontrado, verifica a senha
        if user.check_password(password):
            return user
        return None