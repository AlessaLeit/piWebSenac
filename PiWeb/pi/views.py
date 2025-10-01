import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from twilio.rest import Client
from .models import Pedido, Pizza, Usuario

def login(request):
    if request.method == "POST":
        id = request.POST.get("id")
        senha = request.POST.get("senha")

        try:
            user = Usuario.objects.get(cpf=id)
        except Usuario.DoesNotExist:
            try:
                user = Usuario.objects.get(telefone=id)
            except Usuario.DoesNotExist:
                user = None

        if user and user.check_password(senha):
            login(request, user)
            return redirect("pedido:selecionar_tamanho")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            return render(request, "login.html", {"erro": "Usuário ou senha inválidos."})

    return render(request, "login.html")

def cadastrar(request): 
    if request.method == "POST":
        nome = request.POST.get("nome")
        cpf = request.POST.get("cpf")
        telefone = request.POST.get("telefone")
        endereco = request.POST.get("endereco")
        senha = request.POST.get("senha")
        confirmarsenha = request.POST.get("confirmarsenha")

        if senha != confirmarsenha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "cadastro.html")

        if not cpf or not telefone or not senha:
            messages.error(request, "CPF, telefone e senha são obrigatórios.")
            return render(request, "cadastro.html")

        from .models import Usuario
        if Usuario.objects.filter(cpf=cpf).exists():
            messages.error(request, "CPF já cadastrado.")
            return render(request, "cadastro.html")

        if Usuario.objects.filter(telefone=telefone).exists():
            messages.error(request, "Telefone já cadastrado.")
            return render(request, "cadastro.html")

        usuario = Usuario.objects.create_user(
            username=cpf,
            cpf=cpf,
            telefone=telefone,
            endereco=endereco,
            password=senha,
            first_name=nome
        )
        usuario.save()

        messages.success(request, "Cadastro realizado com sucesso. Faça login.")
        return redirect('pedido:login')
   
    return render(request, "cadastro.html")
            
def selecionar_tamanho(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    pedido_atual = json.loads(request.COOKIES.get('pedido_atual', '{}'))
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'
    adicionando = request.GET.get('adicionando') or request.POST.get('adicionando') == 'true'
    from_page = request.GET.get('from')

    tamanho_selecionado = pedido_atual.get('tamanho')

    if request.method == "POST":
        tamanho = request.POST.get('tamanho')
        if not tamanho:
            response = render(request, 'pedido/tamanho.html', {
                'etapa': 'tamanho',
                'erro': 'Por favor, selecione um tamanho.',
                'pedido': pedido_atual,
                'editando': editando,
                'adicionando': adicionando,
                'tamanho_selecionado': tamanho_selecionado
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        # salva no pedido atual, mas não joga em pedidos ainda
        pedido_atual['tamanho'] = tamanho

        # Redireciona para a página apropriada com base no tamanho
        if tamanho == 'Calzone':
            redirect_view = 'pedido:selecionar_sabores_calzone'
        else:
            redirect_view = 'pedido:selecionar_sabores'

        flag = 'editando=true' if editando else ('adicionando=true' if adicionando else '')
        if editando and from_page:
            flag += f'&from={from_page}'
        response = redirect(reverse(redirect_view) + ('?' + flag if flag else ''))
        response.set_cookie('pedido_atual', json.dumps(pedido_atual))
        response.set_cookie('pedidos', json.dumps(pedidos))
        return response

    response = render(request, 'pedido/tamanho.html', {
        'etapa': 'tamanho',
        'pedido': pedido_atual,
        'editando': editando,
        'adicionando': adicionando,
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
    adicionando = request.GET.get('adicionando') or request.POST.get('adicionando') == 'true'
    from_page = request.GET.get('from')

    sabores_selecionados = pedido_atual.get('sabores', [])

    if request.method == "POST":
        sabores = request.POST.getlist('sabores')
        if not sabores:
            response = render(request, 'pedido/sabores.html', {
                'etapa': 'sabores',
                'erro': 'Selecione pelo menos um sabor.',
                'pedido': pedido_atual,
                'editando': editando,
                'adicionando': adicionando,
                'sabores_selecionados': sabores_selecionados
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        # Validação de quantidade de sabores por tamanho
        tamanho = pedido_atual.get('tamanho', '')
        max_sabores = 3  # padrão para pizzas

        if tamanho in ['Média', 'Grande', 'Big']:
            max_sabores = 3
        else:
            max_sabores = 3  # fallback

        if len(sabores) > max_sabores:
            erro_msg = f"Erro: {tamanho} permite no máximo {max_sabores} sabores."

            response = render(request, 'pedido/sabores.html', {
                'etapa': 'sabores',
                'erro': erro_msg,
                'pedido': pedido_atual,
                'editando': editando,
                'adicionando': adicionando,
                'sabores_selecionados': sabores_selecionados
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        pedido_atual['sabores'] = sabores

        if not editando:
            response = redirect('pedido:confirmar_adicionar')
        else:
            pedidos.append(pedido_atual)
            pedido_atual = {}
            if from_page == 'confirmar_adicionar':
                response = redirect('pedido:confirmar_adicionar')
            else:
                response = redirect('pedido:revisar_pedido')
        response.set_cookie('pedido_atual', json.dumps(pedido_atual))
        response.set_cookie('pedidos', json.dumps(pedidos))
        return response

    response = render(request, 'pedido/sabores.html', {
        'etapa': 'sabores',
        'pedido': pedido_atual,
        'editando': editando,
        'adicionando': adicionando,
        'sabores_selecionados': sabores_selecionados
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('pedido_atual', json.dumps(pedido_atual))
    return response

def selecionar_sabores_calzone(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    index = request.GET.get('index')  # para edição
    pedido_atual = pedidos[int(index)] if index is not None else json.loads(request.COOKIES.get('pedido_atual', '{}'))
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'
    adicionando = request.GET.get('adicionando') or request.POST.get('adicionando') == 'true'
    from_page = request.GET.get('from')

    sabores_selecionados = pedido_atual.get('sabores', [])

    if request.method == "POST":
        sabores = request.POST.getlist('sabores')
        if not sabores:
            response = render(request, 'pedido/sabores_calzone.html', {
                'etapa': 'sabores',
                'erro': 'Selecione um sabor.',
                'pedido': pedido_atual,
                'editando': editando,
                'adicionando': adicionando,
                'sabores_selecionados': sabores_selecionados
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        # Calzone permite apenas 1 sabor
        if len(sabores) > 1:
            response = render(request, 'pedido/sabores_calzone.html', {
                'etapa': 'sabores',
                'erro': 'Erro: Calzone permite apenas 1 sabor.',
                'pedido': pedido_atual,
                'editando': editando,
                'adicionando': adicionando,
                'sabores_selecionados': sabores_selecionados
            })
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            return response

        pedido_atual['sabores'] = sabores

        if not editando:
            response = redirect('pedido:confirmar_adicionar')
        else:
            pedidos.append(pedido_atual)
            pedido_atual = {}
            if from_page == 'confirmar_adicionar':
                response = redirect('pedido:confirmar_adicionar')
            else:
                response = redirect('pedido:revisar_pedido')
        response.set_cookie('pedido_atual', json.dumps(pedido_atual))
        response.set_cookie('pedidos', json.dumps(pedidos))
        return response

    response = render(request, 'pedido/sabores_calzone.html', {
        'etapa': 'sabores',
        'pedido': pedido_atual,
        'editando': editando,
        'adicionando': adicionando,
        'sabores_selecionados': sabores_selecionados
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('pedido_atual', json.dumps(pedido_atual))
    return response

def confirmar_adicionar(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    pedido_atual = json.loads(request.COOKIES.get('pedido_atual', '{}'))
    observacoes = json.loads(request.COOKIES.get('observacoes', '{}'))

    # Calcula total incluindo pedido_atual se existir
    all_pizzas = pedidos + ([pedido_atual] if pedido_atual.get('tamanho') else [])
    # Adiciona observacao a cada pizza
    for i, p in enumerate(all_pizzas):
        p['observacao'] = observacoes.get(str(i), '')
    total = 0
    for p in all_pizzas:
        tamanho = p.get('tamanho')
        if tamanho == "Média":
            total += 50
        elif tamanho == "Grande":
            total += 60
        elif tamanho == "Big":
            total += 70
        elif tamanho == "Calzone":
            total += 75

    # Excluir pizza pelo índice
    excluir_index = request.GET.get('excluir')
    if excluir_index is not None:
        try:
            excluir_index = int(excluir_index)
            if excluir_index < len(pedidos):
                del pedidos[excluir_index]
                # Remove a observação correspondente
                if str(excluir_index) in observacoes:
                    del observacoes[str(excluir_index)]
            elif excluir_index == len(pedidos) and pedido_atual.get('tamanho'):
                pedido_atual = {}
                # Remove a observação do pedido_atual
                if str(excluir_index) in observacoes:
                    del observacoes[str(excluir_index)]
        except (ValueError, IndexError):
            pass
        response = redirect('pedido:confirmar_adicionar')
        response.set_cookie('pedidos', json.dumps(pedidos))
        response.set_cookie('pedido_atual', json.dumps(pedido_atual))
        response.set_cookie('observacoes', json.dumps(observacoes))
        return response

    # Editar pizza pelo índice
    editar_index = request.GET.get('editar')
    if editar_index is not None:
        try:
            editar_index = int(editar_index)
            if editar_index < len(pedidos):
                # carrega pizza no pedido_atual e remove da lista
                pedido_atual = pedidos.pop(editar_index)
                # Remove a observação correspondente
                if str(editar_index) in observacoes:
                    del observacoes[str(editar_index)]
            elif editar_index == len(pedidos) and pedido_atual.get('tamanho'):
                # Remove a observação do pedido_atual
                if str(editar_index) in observacoes:
                    del observacoes[str(editar_index)]
            response = redirect(reverse('pedido:selecionar_tamanho') + '?editando=true&from=confirmar_adicionar')
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('observacoes', json.dumps(observacoes))
            return response
        except (ValueError, IndexError):
            pass

    if request.method == "POST":
        action = request.POST.get('action')

        # Processa as observações do formulário
        for i in range(len(all_pizzas)):
            obs_key = f'observacoes_{i}'
            if obs_key in request.POST:
                observacoes[str(i)] = request.POST[obs_key].strip()

        if action == "add":
            if pedido_atual.get('tamanho'):
                pedidos.append(pedido_atual)
            pedido_atual = {}
            response = redirect(reverse('pedido:selecionar_tamanho') + '?adicionando=true')  # inicia nova pizza
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            response.set_cookie('observacoes', json.dumps(observacoes))
            return response
        elif action == "proceed":
            if pedido_atual.get('tamanho'):
                pedidos.append(pedido_atual)
            pedido_atual = {}
            response = redirect('pedido:selecionar_pagamento')  # vai pagar todas
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            response.set_cookie('observacoes', json.dumps(observacoes))
            return response
        elif action == "back":
            response = redirect('pedido:selecionar_sabores')
            response.set_cookie('pedidos', json.dumps(pedidos))
            response.set_cookie('pedido_atual', json.dumps(pedido_atual))
            response.set_cookie('observacoes', json.dumps(observacoes))
            return response

    response = render(request, 'pedido/confirmar_adicionar.html', {
        'all_pizzas': all_pizzas,
        'total': total,
        'observacoes': observacoes
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('pedido_atual', json.dumps(pedido_atual))
    response.set_cookie('observacoes', json.dumps(observacoes))
    return response

def selecionar_pagamento(request):
    pedidos = json.loads(request.COOKIES.get('pedidos', '[]'))
    order = json.loads(request.COOKIES.get('order', '{}'))
    observacoes = json.loads(request.COOKIES.get('observacoes', '{}'))
    editando = request.GET.get('editando') == 'true'
    adicionando = request.GET.get('adicionando') == 'true'

    # Adiciona observacao a cada pizza
    for i, p in enumerate(pedidos):
        p['observacao'] = observacoes.get(str(i), '')

    # calcula total do pedido somando todos
    total = 0
    for p in pedidos:
        tamanho = p.get('tamanho')
        if tamanho == "Média":
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
                'editando': editando,
                'adicionando': adicionando
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
        'editando': editando,
        'adicionando': adicionando
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
    try:
        observacoes = json.loads(request.COOKIES.get('observacoes', '{}'))
    except (json.JSONDecodeError, TypeError):
        observacoes = {}
    pagamento = order.get('pagamento')

    # Excluir pizza pelo índice
    excluir_index = request.GET.get('excluir')
    if excluir_index is not None:
        try:
            excluir_index = int(excluir_index)
            if 0 <= excluir_index < len(pedidos):
                del pedidos[excluir_index]
                # Remove a observação correspondente
                if str(excluir_index) in observacoes:
                    del observacoes[str(excluir_index)]
        except (ValueError, IndexError):
            pass
        response = redirect('pedido:revisar_pedido')
        response.set_cookie('pedidos', json.dumps(pedidos))
        response.set_cookie('order', json.dumps(order))
        response.set_cookie('observacoes', json.dumps(observacoes))
        return response

    # Editar pizza pelo índice
    editar_index = request.GET.get('editar')
    if editar_index is not None:
        try:
            editar_index = int(editar_index)
            if 0 <= editar_index < len(pedidos):
                # carrega pizza no pedido_atual e remove da lista
                pedido_atual = pedidos.pop(editar_index)
                # Remove a observação correspondente
                if str(editar_index) in observacoes:
                    del observacoes[str(editar_index)]
                response = redirect(reverse('pedido:selecionar_tamanho') + '?editando=true&from=revisao')
                response.set_cookie('pedido_atual', json.dumps(pedido_atual))
                response.set_cookie('pedidos', json.dumps(pedidos))
                response.set_cookie('order', json.dumps(order))
                response.set_cookie('observacoes', json.dumps(observacoes))
                return response
        except (ValueError, IndexError):
            pass

    # calcula total
    total = 0
    for p in pedidos:
        if p['tamanho'] == "Média":
            total += 50.00
        elif p['tamanho'] == "Grande":
            total += 60.00
        elif p['tamanho'] == "Big":
            total += 70.00
        elif p['tamanho'] == "Calzone":
            total += 75.00

    if request.method == "POST":
        # Update observacoes from POST data
        for i in range(len(pedidos)):
            obs_key = f'observacoes_{i}'
            if obs_key in request.POST:
                observacoes[str(i)] = request.POST[obs_key].strip()

        # Salva no banco de dados
        pedido = Pedido.objects.create(
            nome=order.get('nome'),
            telefone=order.get('telefone'),
            endereco=order.get('endereco'),
            retirada=order.get('retirada', False),
            pagamento=order.get('pagamento')
        )
        for i, p in enumerate(pedidos):
            obs_key = str(i)
            observacao = observacoes.get(obs_key, '').strip()
            Pizza.objects.create(
                pedido=pedido,
                tamanho=p['tamanho'],
                sabores=','.join(p['sabores']),
                observacao=observacao
            )

        # Formatar mensagem para WhatsApp
        pizzas_str = []
        for i, p in enumerate(pedidos, 1):
            obs_key = str(i - 1)
            observacao = observacoes.get(obs_key, '').strip()

            tamanho = p['tamanho']
            if tamanho in ['Média', 'Grande', 'Big']:
                tipo_item = f"Pizza {tamanho}"
            else:
                tipo_item = tamanho.capitalize()

            pizza_line = (
                f"*Detalhes do Pedido {i}*\n"
                f"- {tipo_item}\n"
                f"- Sabores: {', '.join(p['sabores'])}\n"
                f"- Observações: {observacao if observacao else 'Nenhuma'}\n"
            )
            pizzas_str.append(pizza_line)

        pizzas_text = '\n'.join(pizzas_str)

        message = (
            f"Olá, me chamo *{order.get('nome')}*!\n\n"
            f"{pizzas_text}\n"
            f"*Detalhes Gerais*\n"
            f"- Valor: R$ {total:.2f}\n"
            f"- Pagamento: {pagamento}\n"
            f"- Endereço: {order.get('endereco')}"
        )

        import urllib.parse
        msg_encoded = urllib.parse.quote(message)

        # Redirecionar para link do WhatsApp
        url_whatsapp = f"https://wa.me/5547997582686?text={msg_encoded}"
        return redirect(url_whatsapp)

    # Adiciona observacao a cada pizza
    for i, p in enumerate(pedidos):
        p['observacao'] = observacoes.get(str(i), '')

    success = request.GET.get('success') == 'true'
    response = render(request, 'pedido/revisao.html', {
        'pedidos': pedidos,
        'total': total,
        'pagamento': pagamento,
        'pedido': order,
        'etapa': 'revisao',
        'success': success,
        'observacoes': observacoes
    })
    response.set_cookie('pedidos', json.dumps(pedidos))
    response.set_cookie('order', json.dumps(order))
    response.set_cookie('observacoes', json.dumps(observacoes))
    return response



