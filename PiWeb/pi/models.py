from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Campos personalizados
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return self.username
