from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.first_name or self.username

class Pedido(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    retirada = models.BooleanField(default=False)
    pagamento = models.CharField(max_length=50)

    def __str__(self):
        return f"Pedido #{self.id} - {self.nome}"


class Pizza(models.Model):
    TAMANHOS = [
        ("Media", "Média"),
        ("Grande", "Grande"),
        ("Big", "Big"),
        ("Calzone", "Calzone"),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="pizzas")
    tamanho = models.CharField(max_length=20, choices=TAMANHOS)
    sabores = models.TextField(help_text="Lista de sabores separados por vírgula")
    observacao = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.tamanho} - {self.sabores}"
