from django.shortcuts import render, redirect

def selecionar_tamanho(request):
    pizzas = request.session.get('pizzas', [])
    pizza_index = request.GET.get('pizza_index')
    if pizza_index is not None:
        pizza_index = int(pizza_index)
        current_pizza = pizzas[pizza_index] if pizza_index < len(pizzas) else {}
    else:
        current_pizza = request.session.get('current_pizza', {})
        pizza_index = None  # New pizza

    tamanho_selecionado = current_pizza.get('tamanho')

    if request.method == "POST":
        tamanho = request.POST.get('tamanho')
        if not tamanho:
            return render(request, 'pedido/tamanho.html', {
                'etapa': 'tamanho',
                'erro': 'Por favor, selecione um tamanho.',
                'current_pizza': current_pizza,
                'tamanho_selecionado': tamanho_selecionado,
                'pizza_index': pizza_index
            })

        current_pizza['tamanho'] = tamanho
        if pizza_index is not None:
            pizzas[pizza_index] = current_pizza
        else:
            request.session['current_pizza'] = current_pizza
        request.session['pizzas'] = pizzas

        return redirect('pedido:selecionar_sabores')

    return render(request, 'pedido/tamanho.html', {
        'etapa': 'tamanho',
        'current_pizza': current_pizza,
        'tamanho_selecionado': tamanho_selecionado,
        'pizza_index': pizza_index
    })

def selecionar_sabores(request):
    pizzas = request.session.get('pizzas', [])
    pizza_index = request.GET.get('pizza_index')
    if pizza_index is not None:
        pizza_index = int(pizza_index)
        current_pizza = pizzas[pizza_index] if pizza_index < len(pizzas) else {}
    else:
        current_pizza = request.session.get('current_pizza', {})

    sabores_selecionados = current_pizza.get('sabores', [])

    if request.method == "POST":
        sabores = request.POST.getlist('sabores')
        if not sabores:
            return render(request, 'pedido/sabores.html', {
                'etapa': 'sabores',
                'erro': 'Selecione pelo menos um sabor.',
                'current_pizza': current_pizza,
                'sabores_selecionados': sabores_selecionados,
                'pizza_index': pizza_index
            })

        current_pizza['sabores'] = sabores
        if pizza_index is not None:
            pizzas[pizza_index] = current_pizza
        else:
            pizzas.append(current_pizza)
            request.session['current_pizza'] = {}  # Reset for next
        request.session['pizzas'] = pizzas

        return redirect('pedido:confirmar_adicionar_pizza')

    return render(request, 'pedido/sabores.html', {
        'etapa': 'sabores',
        'current_pizza': current_pizza,
        'sabores_selecionados': sabores_selecionados,
        'pizza_index': pizza_index
    })

def confirmar_adicionar_pizza(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            return redirect('pedido:selecionar_tamanho')
        elif action == 'proceed':
            return redirect('pedido:selecionar_pagamento')
    return render(request, 'pedido/confirmar_adicionar.html', {'etapa': 'confirmar'})

def selecionar_pagamento(request):
    pizzas = request.session.get('pizzas', [])
    pagamento = request.session.get('pagamento')
    endereco = request.session.get('endereco')

    if request.method == "POST":
        pagamento = request.POST.get('pagamento')
        if not pagamento:
            return render(request, 'pedido/pagamento.html', {
                'etapa': 'pagamento',
                'erro': 'Selecione uma forma de pagamento.',
                'pagamento_selecionado': pagamento
            })

        request.session['pagamento'] = pagamento
        return redirect('pedido:selecionar_endereco')

    return render(request, 'pedido/pagamento.html', {
        'etapa': 'pagamento',
        'pagamento_selecionado': pagamento
    })

def selecionar_endereco(request):
    endereco = request.session.get('endereco', '')
    if not endereco:
        endereco = 'Retirar no balcão'

    if request.method == "POST":
        endereco = request.POST.get('endereco', '').strip()
        if not endereco:
            endereco = 'Retirar no balcão'

        request.session['endereco'] = endereco
        return redirect('pedido:revisar_pedido')

    return render(request, 'pedido/endereco.html', {
        'etapa': 'endereco',
        'endereco_selecionado': endereco
    })

def revisar_pedido(request):
    pizzas = request.session.get('pizzas', [])
    pagamento = request.session.get('pagamento')
    endereco = request.session.get('endereco')

    # Handle editing
    pizza_index = request.GET.get('pizza_index')
    campo_editar = request.GET.get('editar')
    if campo_editar:
        if campo_editar in ['pagamento', 'endereco']:
            if campo_editar == 'pagamento':
                del request.session['pagamento']
            elif campo_editar == 'endereco':
                del request.session['endereco']
            etapas = {
                'pagamento': 'pedido:selecionar_pagamento',
                'endereco': 'pedido:selecionar_endereco'
            }
            return redirect(etapas.get(campo_editar, 'pedido:revisar_pedido'))
        elif pizza_index is not None:
            pizza_index = int(pizza_index)
            if campo_editar in ['tamanho', 'sabores']:
                if campo_editar == 'tamanho':
                    pizzas[pizza_index].pop('tamanho', None)
                elif campo_editar == 'sabores':
                    pizzas[pizza_index].pop('sabores', None)
                request.session['pizzas'] = pizzas
                etapas = {
                    'tamanho': 'pedido:selecionar_tamanho',
                    'sabores': 'pedido:selecionar_sabores'
                }
                return redirect(etapas[campo_editar] + f'?pizza_index={pizza_index}')

    # Check if all required data is present
    if not pizzas or not all(p.get('tamanho') and p.get('sabores') for p in pizzas) or not pagamento or not endereco:
        return redirect('pedido:selecionar_tamanho')

    if request.method == "POST":
        # Finaliza o pedido e limpa a sessão
        request.session.flush()
        return render(request, 'pedido/finalizado.html', {
            'pizzas': pizzas,
            'pagamento': pagamento,
            'endereco': endereco,
            'etapa': 'finalizado'
        })

    return render(request, 'pedido/revisao.html', {
        'pizzas': pizzas,
        'pagamento': pagamento,
        'endereco': endereco,
        'etapa': 'revisao'
    })
