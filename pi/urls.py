# pedido/urls.py
from django.urls import path
from . import views

app_name = 'pedido'

urlpatterns = [
    # pedido
    path('tamanho/', views.selecionar_tamanho, name='selecionar_tamanho'),
    path('sabores/', views.selecionar_sabores, name='selecionar_sabores'),
    path('sabores_calzone/', views.selecionar_sabores_calzone, name='selecionar_sabores_calzone'),
    path('pagamento/', views.selecionar_pagamento, name='selecionar_pagamento'),
    path('endereco/', views.selecionar_endereco, name='selecionar_endereco'),
    path('revisao/', views.revisar_pedido, name='revisar_pedido'),
    path('confirmar_adicionar/', views.confirmar_adicionar, name='confirmar_adicionar'),
    path('login/', views.login , name='login'),
    path('cadastro/', views.cadastrar, name='cadastrar'),
    path('resetar_senha/', views.resetar_senha, name='resetar_senha'),
    path('confirmar_reset_senha/<uidb64>/<token>/', views.confirmar_reset_senha, name='confirmar_reset_senha'),
    path('logout/', views.logout, name='logout'),
    path('perfil/', views.editar_perfil, name='editar_perfil'),
]
