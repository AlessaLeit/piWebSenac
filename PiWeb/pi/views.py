import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from twilio.rest import Client
from .models import Pedido, Pizza

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # user = authenticate(request, username=username, password=password)

        #if user is not None:
           # login(request, user)
            #return redirect("selecionar_tamanho")  
        #else:
            #messages.error(request, "Usuário ou senha inválidos.")
        
        if username and password:
            request.session["usuario"] = username  # salva na sessão
            return redirect('pedido:selecionar_tamanho')
        else:
            return render(request, "login.html", {"erro": "Preencha usuário e senha!"})
   
    return render(request, "login.html")
    
def selecionar_tamanho(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    pedido_atual = json.loads(request.COOKIES.get('pedido_atual', '{}'))  # sempre trabalhar no temporário
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'

    tamanho_selecionado = pedido_atual.get('tamanho')

    if request.method == "POST":
        tamanho = request.POST.get('tamanho')
        if not tamanho:
            response = render(request, 'pedido/tamanho.html', {
                'etapa': 'tamanho',
                'erro': 'Por favor, selecione um tamanho.',
                'pedido': pedido_atual,
                'editando': editando,
                'tamanho_selecionado': tamanho_selecionado
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        # salva no pedido atual, mas não joga em pedidos ainda
        pedido_atual['tamanho'] = tamanho

        response = redirect('pedido:selecionar_sabores' if not editando else 'pedido:revisar_pedido')
        response.set_cookie('pedido_atual', json.dumps(pedido_atual))
        response.set_cookie('pedidos', json.dumps(pedidos))
        return response

    response = render(request, 'pedido/tamanho.html', {
        'etapa': 'tamanho',
        'pedido': pedido_atual,
        'editando': editando,
        'tamanho_selecionado': tamanho_selecionado
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('pedido_atual', json.dumps(pedido_atual))
    return response

def selecionar_sabores(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    index = request.GET.get('index')  # para edição
    pedido_atual = pedidos[int(index)] if index is not None else json.loads(request.COOKIES.get('pedido_atual', '{}'))
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'

    sabores_selecionados = pedido_atual.get('sabores', [])

    if request.method == "POST":
        sabores = request.POST.getlist('sabores')
        if not sabores:
            response = render(request, 'pedido/sabores.html', {
                'etapa': 'sabores',
                'erro': 'Selecione pelo menos um sabor.',
                'pedido': pedido_atual,
                'editando': editando,
                'sabores_selecionados': sabores_selecionados
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        pedido_atual['sabores'] = sabores

        response = redirect('pedido:confirmar_adicionar' if not editando else 'pedido:revisar_pedido')
        response.set_cookie('pedido_atual', json.dumps(pedido_atual))
        response.set_cookie('pedidos', json.dumps(pedidos))
        return response

    response = render(request, 'pedido/sabores.html', {
        'etapa': 'sabores',
        'pedido': pedido_atual,
        'editando': editando,
        'sabores_selecionados': sabores_selecionados
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('pedido_atual', json.dumps(pedido_atual))
    return response

def confirmar_adicionar(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    pedido_atual = json.loads(request.COOKIES.get('pedido_atual', '{}'))

    # Calcula total incluindo pedido_atual se existir
    all_pizzas = pedidos + ([pedido_atual] if pedido_atual.get('tamanho') else [])
    total = 0
    for p in all_pizzas:
        tamanho = p.get('tamanho')
        if tamanho == "Media":
            total += 50
        elif tamanho == "Grande":
            total += 60
        elif tamanho == "Big":
            total += 70
        elif tamanho == "Calzone":
            total += 75

    if request.method == "POST":
        action = request.POST.get('action')
        if action == "add":
            if pedido_atual.get('tamanho'):
                pedidos.append(pedido_atual)
            pedido_atual = {}
            response = redirect('pedido:selecionar_tamanho')  # inicia nova pizza
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response
        elif action == "proceed":
            if pedido_atual.get('tamanho'):
                pedidos.append(pedido_atual)
            pedido_atual = {}
            response = redirect('pedido:selecionar_pagamento')  # vai pagar todas
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

    response = render(request, 'pedido/confirmar_adicionar.html', {
        'pedidos': pedidos,
        'pedido_atual': pedido_atual,
        'total': total
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('pedido_atual', json.dumps(pedido_atual))
    return response

def selecionar_pagamento(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    order = json.loads(request.COOKIES.get('order', '{}'))
    editando = request.GET.get('editando') == 'true'

    # calcula total do pedido somando todos
    total = 0
    for p in pedidos:
        tamanho = p.get('tamanho')
        if tamanho == "Media":
            total += 50
        elif tamanho == "Grande":
            total += 60
        elif tamanho == "Big":
            total += 70
        elif tamanho == "Calzone":
            total += 75

    pagamento_selecionado = order.get('pagamento')

    if request.method == "POST":
        pagamento = request.POST.get('pagamento')
        if not pagamento:
            response = render(request, 'pedido/pagamento.html', {
                'etapa': 'pagamento',
                'erro': 'Selecione uma forma de pagamento.',
                'pedidos': pedidos,
                'total': total,
                'pagamento_selecionado': pagamento_selecionado,
                'editando': editando
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('order', json.dumps(order))
            return response

        order['pagamento'] = pagamento

        if editando:
            response = redirect('pedido:revisar_pedido')
        else:
            response = redirect('pedido:selecionar_endereco')
        response.set_cookie('order', json.dumps(order))
        response.set_cookie('pedidos', json.dumps(pedidos))
        return response

    response = render(request, 'pedido/pagamento.html', {
        'etapa': 'pagamento',
        'pedidos': pedidos,
        'total': total,
        'pagamento_selecionado': pagamento_selecionado,
        'editando': editando
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('order', json.dumps(order))
    return response

def selecionar_endereco(request):
    order = json.loads(request.COOKIES.get('order', '{}'))

    if request.method == "POST":
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco', '').strip()
        retirada = request.POST.get('retirada') == 'on'

        if retirada:
            endereco = 'Retirar no balcão'

        order['nome'] = nome
        order['telefone'] = telefone
        order['endereco'] = endereco
        order['retirada'] = retirada

        response = redirect('pedido:revisar_pedido')
        response.set_cookie('order', json.dumps(order))
        return response

    response = render(request, 'pedido/endereco.html', {
        'etapa': 'endereco',
        'pedido': order
    })
    response.set_cookie('order', json.dumps(order))
    return response

def revisar_pedido(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    order = json.loads(request.COOKIES.get('order', '{}'))
    pagamento = order.get('pagamento')

    # Excluir pizza pelo índice
    excluir_index = request.GET.get('excluir')
    if excluir_index is not None:
        try:
            excluir_index = int(excluir_index)
            if 0 <= excluir_index < len(pedidos):
                del pedidos[excluir_index]
        except (ValueError, IndexError):
            pass
        response = redirect('pedido:revisar_pedido')
        response.set_cookie('pedidos', json.dumps(pedidos))
        response.set_cookie('order', json.dumps(order))
        return response

    # Editar pizza pelo índice
    editar_index = request.GET.get('editar')
    if editar_index is not None:
        try:
            editar_index = int(editar_index)
            if 0 <= editar_index < len(pedidos):
                # carrega pizza no pedido_atual e remove da lista
                pedido_atual = pedidos.pop(editar_index)
                response = redirect('pedido:selecionar_tamanho')
                response.set_cookie('pedido_atual', json.dumps(pedido_atual))
                response.set_cookie('pedidos', json.dumps(pedidos))
                response.set_cookie('order', json.dumps(order))
                return response
        except (ValueError, IndexError):
            pass

    # calcula total
    total = 0
    for p in pedidos:
        if p['tamanho'] == "Media":
            total += 50.00
        elif p['tamanho'] == "Grande":
            total += 60.00
        elif p['tamanho'] == "Big":
            total += 70.00
        elif p['tamanho'] == "Calzone":
            total += 75.00

    if request.method == "POST":
        # Salva no banco de dados
        pedido = Pedido.objects.create(
            nome=order.get('nome'),
            telefone=order.get('telefone'),
            endereco=order.get('endereco'),
            retirada=order.get('retirada', False),
            pagamento=order.get('pagamento')
        )
        for p in pedidos:
            Pizza.objects.create(
                pedido=pedido,
                tamanho=p['tamanho'],
                sabores=','.join(p['sabores'])
            )

        # Formatar mensagem para WhatsApp
        pizzas_str = '\n'.join([f"🍕 *{p['tamanho']}* com  {', '.join(p['sabores'])} " for p in pedidos])

        message = (
            f"👋 *Olá {order.get('nome')}!*\n\n"
            f"*Detalhes do pedido:*\n{pizzas_str}\n\n"
            f"💵 *Total:* R$ {total:.2f}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"📍 *Endereço:* {order.get('endereco')}\n\n"
            "Obrigado por pedir com a gente! 🚀"
        )

        import urllib.parse
        msg_encoded = urllib.parse.quote(message)

        # Redirecionar para link do WhatsApp
        url_whatsapp = f"https://wa.me/5547989036464?text={msg_encoded}"
        return redirect(url_whatsapp)

    success = request.GET.get('success') == 'true'
    response = render(request, 'pedido/revisao.html', {
        'pedidos': pedidos,
        'total': total,
        'pagamento': pagamento,
        'pedido': order,
        'etapa': 'revisao',
        'success': success
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('order', json.dumps(order))
    return response


