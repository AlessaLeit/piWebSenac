# pedido/urls.py
from django.urls import path
from . import views

app_name = 'pedido'

urlpatterns = [
    # pedido
    path('tamanho/', views.selecionar_tamanho, name='selecionar_tamanho'),
    path('sabores/', views.selecionar_sabores, name='selecionar_sabores'),
    path('pagamento/', views.selecionar_pagamento, name='selecionar_pagamento'),
    path('endereco/', views.selecionar_endereco, name='selecionar_endereco'),
    path('revisao/', views.revisar_pedido, name='revisar_pedido'),
    path('confirmar_adicionar/', views.confirmar_adicionar, name='confirmar_adicionar'),
]
