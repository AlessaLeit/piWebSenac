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
    # edição
    path('editar/tamanho/', views.editar_tamanho, name='editar_tamanho'),
    path('editar/sabores/', views.editar_sabores, name='editar_sabores'),
    path('editar/pagamento/', views.editar_pagamento, name='editar_pagamento'),
    path('editar/endereco/', views.editar_endereco, name='editar_endereco'),
]
