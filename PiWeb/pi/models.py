from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    nome = models.CharField(max_length=100, blank=True)

    # Remove unused inherited fields
    first_name = None
    last_name = None
    email = None

    def __str__(self):
        return self.nome or self.username
