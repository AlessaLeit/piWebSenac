from django.db import models

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

    def __str__(self):
        return f"{self.tamanho} - {self.sabores}"
