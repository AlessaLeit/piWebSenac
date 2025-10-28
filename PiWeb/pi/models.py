from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, cpf, email, first_name, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O CPF é obrigatório')
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(cpf=cpf, email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, email, first_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(cpf, email, first_name, password, **extra_fields)

class Usuario(AbstractUser):
    # Remove o campo username padrão, pois usaremos o CPF.
    username = None

    # Campos personalizados
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True)

    # Define o CPF como o campo de login
    USERNAME_FIELD = 'cpf'
    # Campos obrigatórios ao criar um superusuário via 'createsuperuser'
    REQUIRED_FIELDS = ['first_name', 'email']

    objects = UsuarioManager()

    def __str__(self):
        return self.first_name or self.cpf
