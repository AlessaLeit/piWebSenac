import json
import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.core.validators import EmailValidator, ValidationError
from django.contrib.auth.decorators import login_required
from .models import Usuario

def validar_cpf(cpf):
    """Valida CPF brasileiro com algoritmo de checksum."""
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    def calcular_digito(cpf, peso):
        soma = sum(int(d) * p for d, p in zip(cpf, peso))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    primeiro_digito = calcular_digito(cpf[:9], range(10, 1, -1))
    if primeiro_digito != int(cpf[9]):
        return False
    segundo_digito = calcular_digito(cpf[:10], range(11, 1, -1))
    return segundo_digito == int(cpf[10])

def validar_telefone(telefone):
    """Valida formato brasileiro de telefone: (XX) XXXXX-XXXX."""
    pattern = r'^\(\d{2}\)\s\d{4,5}-\d{4}$'
    return bool(re.match(pattern, telefone))

def validar_email(email):
    """Valida email usando Django EmailValidator."""
    try:
        EmailValidator()(email)
        return True
    except ValidationError:
        return False

def validar_senha(senha):
    """Valida força da senha: min 8 chars, maiúscula, minúscula, número."""
    if len(senha) < 8:
        return False
    if not re.search(r'[a-z]', senha):
        return False
    if not re.search(r'[A-Z]', senha):
        return False
    if not re.search(r'\d', senha):
        return False
    return True

def login(request):
    if request.method == "POST":
        id = request.POST.get("id")
        senha = request.POST.get("senha")

        # Limpar CPF para autenticação (remover pontos e traço)
        cpf_limpo = ''.join(filter(str.isdigit, id))

        # A função authenticate agora usará nosso backend customizado.
        # O primeiro argumento para authenticate é sempre 'username', por isso passamos 'cpf_limpo' como 'username'.
        user = authenticate(request, username=cpf_limpo, password=senha)

        if user is not None:
            # Se já há um usuário logado, fazer logout e limpar cookies
            if request.user.is_authenticated:
                auth_logout(request)
                response = redirect('pedido:login')
                response.delete_cookie('pedidos')
                response.delete_cookie('pedido_atual')
                response.delete_cookie('observacoes')
                response.delete_cookie('order')
                return response
            auth_login(request, user)
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
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmarsenha = request.POST.get("confirmarsenha")

        # Validações - mostrar apenas o primeiro erro encontrado
        if not nome or len(nome) < 3:
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "Nome deve ter pelo menos 3 caracteres."})

        if not validar_cpf(cpf):
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "CPF inválido."})

        if not validar_telefone(telefone):
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "Telefone inválido. Use o formato (XX) XXXXX-XXXX."})

        if not validar_email(email):
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "Email inválido."})

        if not validar_senha(senha):
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "Senha deve ter pelo menos 8 caracteres, incluindo maiúscula, minúscula e número."})

        if senha != confirmarsenha:
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "As senhas não coincidem."})

        if not cpf or not telefone or not senha or not email:
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "CPF, telefone, email e senha são obrigatórios."})

        from .models import Usuario
        if Usuario.objects.filter(cpf=cpf).exists():
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "CPF já cadastrado."})

        if Usuario.objects.filter(telefone=telefone).exists():
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "Telefone já cadastrado."})

        if Usuario.objects.filter(email=email).exists():
            return render(request, "cadastro.html", {"form_data": request.POST, "erro": "Email já cadastrado."})

        usuario = Usuario.objects.create_user(
            # O username não é mais necessário, pois o USERNAME_FIELD é 'cpf'
            first_name=nome,
            cpf=cpf,
            telefone=telefone,
            endereco=endereco,
            email=email,
            password=senha
        )
        usuario.save()

        # Log in the user automatically after successful registration
        from pi.backends import CPFBackend
        auth_login(request, usuario, backend='pi.backends.CPFBackend')
        return redirect("pedido:selecionar_tamanho")

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
            total += 55
        elif tamanho == "Grande":
            total += 65
        elif tamanho == "Big":
            total += 75
        elif tamanho == "Calzone":
            total += 85

        # Adicionar custo da borda se não for "Sem Borda" e for pizza (não Calzone)
        if tamanho in ['Média', 'Grande', 'Big']:
            borda = p.get('borda', 'Sem Borda')
            if borda and borda != 'Sem Borda':
                total += 15

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
                    del observacoes[str(excluir_index)]
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
            # Processa as bordas do formulário
            borda_key = f'borda_{i}'
            if borda_key in request.POST:
                all_pizzas[i]['borda'] = request.POST[borda_key]

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
            total += 55
        elif tamanho == "Grande":
            total += 65
        elif tamanho == "Big":
            total += 75
        elif tamanho == "Calzone":
            total += 85

        # Adicionar custo da borda se não for "Sem Borda" e for pizza (não Calzone)
        if tamanho in ['Média', 'Grande', 'Big']:
            borda = p.get('borda', 'Sem Borda')
            if borda and borda != 'Sem Borda':
                total += 15

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

    if request.user.is_authenticated:
        if not order.get('nome'):
            order['nome'] = request.user.first_name
        if not order.get('telefone'):
            order['telefone'] = request.user.telefone
        # Pull endereco from DB when delivery is selected (retirada not active)
        if not order.get('retirada', False) and request.user.endereco:
            order['endereco'] = request.user.endereco

    if request.method == "POST":
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco', '').strip()
        retirada = request.POST.get('retirada') == 'on'

        if not retirada and not endereco:
            response = render(request, 'pedido/endereco.html', {
                'etapa': 'endereco',
                'pedido': order,
                'erro': 'O endereço é obrigatório quando não for retirada no balcão.'
            })
            response.set_cookie('order', json.dumps(order))
            return response

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
        'pedido': order,
        'user_endereco': request.user.endereco if request.user.is_authenticated else ''
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
            total += 55.00
        elif p['tamanho'] == "Grande":
            total += 65.00
        elif p['tamanho'] == "Big":
            total += 75.00
        elif p['tamanho'] == "Calzone":
            total += 85.00

        # Adicionar custo da borda se não for "Sem Borda" e for pizza (não Calzone)
        if p['tamanho'] in ['Média', 'Grande', 'Big']:
            borda = p.get('borda', 'Sem Borda')
            if borda and borda != 'Sem Borda':
                total += 15

    if request.method == "POST":
        # Update observacoes from POST data
        for i in range(len(pedidos)):
            obs_key = f'observacoes_{i}'
            if obs_key in request.POST:
                observacoes[str(i)] = request.POST[obs_key].strip()

            # Update bordas from POST data
            borda_key = f'borda_{i}'
            if borda_key in request.POST:
                pedidos[i]['borda'] = request.POST[borda_key]

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

            borda_str = ""
            if tamanho in ['Média', 'Grande', 'Big']:
                borda = p.get('borda', 'Sem borda')
                borda_str = f"- Borda: {borda}\n"

            pizza_line = (
                f"*Detalhes do Pedido {i}*\n"
                f"- {tipo_item}\n"
                f"- Sabores: {', '.join(p['sabores'])}\n"
                f"{borda_str}"
                f"- Observações: {observacao if observacao else 'Nenhuma'}"
            )
            pizzas_str.append(pizza_line)

        pizzas_text = '\n'.join(pizzas_str)

        message = (
            f"Olá, me chamo *{order.get('nome')}*!\n\n"
            f"{pizzas_text}\n"
            f"*Detalhes Gerais*\n"
            f"- Valor da(s) Pizza(s): R$ {total:.2f}\n"
            f"- Pagamento: {pagamento}\n"
            f"- Endereço: {order.get('endereco')}"
        )

        import urllib.parse
        msg_encoded = urllib.parse.quote(message)

        # Redirecionar para link do WhatsApp
        url_whatsapp = f"https://wa.me/5547996312284?text={msg_encoded}"
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

def resetar_senha(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email or not validar_email(email):
            messages.error(request, "Email inválido.")
            return render(request, "nova_senha.html", {"erro": "Email inválido."})

        from .models import Usuario
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "Email não encontrado.")
            return render(request, "nova_senha.html", {"erro": "Email não encontrado."})

        # Use Django's PasswordResetTokenGenerator for secure tokens
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Store uid and token in session for verification
        request.session['reset_uid'] = uid
        request.session['reset_token'] = token

        # Send email
        from django.core.mail import send_mail
        reset_url = request.build_absolute_uri(reverse('pedido:confirmar_reset_senha', kwargs={'uidb64': uid, 'token': token}))
        subject = "Redefinição de Senha - Casa das Pizzas"
        message = f"Olá {user.first_name}!\n\nClique no link abaixo para redefinir sua senha:\n{reset_url}\n\nSe você não solicitou esta redefinição, ignore este email.\n\nAtenciosamente,\nEquipe Casa das Pizzas"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        messages.success(request, f"Email enviado para {email}. Verifique sua caixa de entrada para o link de redefinição.")
        return render(request, "nova_senha.html", {"email_enviado": True})

    return render(request, "nova_senha.html")

def logout(request):
    auth_logout(request)
    response = redirect('pedido:login')
    response.delete_cookie('pedidos')
    response.delete_cookie('pedido_atual')
    response.delete_cookie('observacoes')
    response.delete_cookie('order')
    return response

@login_required
def editar_perfil(request):
    user = request.user

    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        endereco = request.POST.get("endereco")
        email = request.POST.get("email")

        # Validações
        if not nome or len(nome) < 3:
            messages.error(request, "Nome deve ter pelo menos 3 caracteres.")
            return render(request, "perfil.html", {"form_data": request.POST})

        if not validar_telefone(telefone):
            messages.error(request, "Telefone inválido. Use o formato (XX) XXXXX-XXXX.")
            return render(request, "perfil.html", {"form_data": request.POST})

        if not validar_email(email):
            messages.error(request, "Email inválido.")
            return render(request, "perfil.html", {"form_data": request.POST})

        # Verificar se email já existe em outro usuário
        if Usuario.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, "Email já cadastrado por outro usuário.")
            return render(request, "perfil.html", {"form_data": request.POST})

        # Atualizar dados
        user.first_name = nome
        user.telefone = telefone
        user.endereco = endereco
        user.email = email
        user.save()

        # Atualizar dados de entrega no pedido atual se existir
        order = json.loads(request.COOKIES.get('order', '{}'))
        if order:
            order['nome'] = user.first_name
            order['telefone'] = user.telefone
            if user.endereco:
                order['endereco'] = user.endereco

        messages.success(request, "Perfil atualizado com sucesso.")
        response = redirect('pedido:editar_perfil')
        if order:
            response.set_cookie('order', json.dumps(order))
        return response

    # Preencher formulário com dados atuais
    form_data = {
        'nome': user.first_name,
        'telefone': user.telefone,
        'endereco': user.endereco,
        'email': user.email,
        'cpf': user.cpf  # CPF não editável
    }

    return render(request, "perfil.html", {"form_data": form_data})

def confirmar_reset_senha(request, uidb64, token):
    from django.contrib.auth.tokens import PasswordResetTokenGenerator
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    token_generator = PasswordResetTokenGenerator()

    if request.method == "POST":
        nova_senha1 = request.POST.get("nova_senha1")
        nova_senha2 = request.POST.get("nova_senha2")

        if not nova_senha1 or not nova_senha2:
            messages.error(request, "Ambas as senhas são obrigatórias.")
            return render(request, "nova_senha.html", {"erro": "Ambas as senhas são obrigatórias.", "validlink": True})

        if nova_senha1 != nova_senha2:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "nova_senha.html", {"erro": "As senhas não coincidem.", "validlink": True})

        # Validate token and uid
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            messages.error(request, "Link inválido.")
            return render(request, "nova_senha.html", {"erro": "Link inválido.", "validlink": False})

        if not token_generator.check_token(user, token):
            messages.error(request, "Token inválido ou expirado.")
            return render(request, "nova_senha.html", {"erro": "Token inválido ou expirado.", "validlink": False})

        user.set_password(nova_senha1)
        user.save()

        messages.success(request, "Senha alterada com sucesso. Faça login.")
        return redirect('pedido:login')

    # Check if token is valid for GET request
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
        validlink = token_generator.check_token(user, token)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        validlink = False

    return render(request, "nova_senha.html", {"validlink": validlink})
