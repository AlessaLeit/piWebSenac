from django.shortcuts import render, redirect

def selecionar_tamanho(request):
    pedido = request.session.get('pedido', {})
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'
    pedido['tamanho'] = None
        
    tamanho_selecionado = pedido.get('tamanho')

    if request.method == "POST":
        tamanho = request.POST.get('tamanho')
        if not tamanho:
            return render(request, 'pedido/tamanho.html', {
                'etapa': 'tamanho',
                'erro': 'Por favor, selecione um tamanho.',
                'pedido': pedido,
                'editando': editando,
                'tamanho_selecionado': tamanho_selecionado
            })

        pedido['tamanho'] = tamanho
        request.session['pedido'] = pedido

        if editando:
            return redirect('pedido:revisar_pedido')
        return redirect('pedido:selecionar_sabores')

    return render(request, 'pedido/tamanho.html', {
        'etapa': 'tamanho',
        'pedido': pedido,
        'editando': editando,
        'tamanho_selecionado': tamanho_selecionado
    })

def selecionar_sabores(request):
    pedido = request.session.get('pedido', {})
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'
    pedido['sabores'] = None
        
    sabores_selecionados = pedido.get('sabores', [])

    if request.method == "POST":
        sabores = request.POST.getlist('sabores')
        if not sabores:
            return render(request, 'pedido/sabores.html', {
                'etapa': 'sabores',
                'erro': 'Selecione pelo menos um sabor.',
                'pedido': pedido,
                'editando': editando,
                'sabores_selecionados': sabores_selecionados
            })

        pedido['sabores'] = sabores
        request.session['pedido'] = pedido

        if editando:
            return redirect('pedido:revisar_pedido')
        return redirect('pedido:selecionar_pagamento')

    return render(request, 'pedido/sabores.html', {
        'etapa': 'sabores',
        'pedido': pedido,
        'editando': editando,
        'sabores_selecionados': sabores_selecionados
    })

def selecionar_pagamento(request):
    pedido = request.session.get('pedido', {})
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'
    pedido['pagamento'] = None
        
    pagamento_selecionado = pedido.get('pagamento')

    if request.method == "POST":
        pagamento = request.POST.get('pagamento')
        if not pagamento:
            return render(request, 'pedido/pagamento.html', {
                'etapa': 'pagamento',
                'erro': 'Selecione uma forma de pagamento.',
                'pedido': pedido,
                'editando': editando,
                'pagamento_selecionado': pagamento_selecionado
            })

        pedido['pagamento'] = pagamento
        request.session['pedido'] = pedido

        if editando:
            return redirect('pedido:revisar_pedido')
        return redirect('pedido:selecionar_endereco')

    return render(request, 'pedido/pagamento.html', {
        'etapa': 'pagamento',
        'pedido': pedido,
        'editando': editando,
        'pagamento_selecionado': pagamento_selecionado
    })

def selecionar_endereco(request):
    pedido = request.session.get('pedido', {})
    editando = request.GET.get('editando') or request.POST.get('editando') == 'true'        
    endereco_selecionado = pedido.get('endereco')
    pedido['endereco'] = ''
        
    if request.method == "POST":
        endereco = request.POST.get('endereco', '').strip()
        if not endereco:
            endereco = 'Retirar no balcão'

        pedido['endereco'] = endereco
        request.session['pedido'] = pedido
                    
        return redirect('pedido:revisar_pedido')

    return render(request, 'pedido/endereco.html', {
        'etapa': 'endereco',
        'pedido': pedido,
        'editando': editando,
        'endereco_selecionado': endereco_selecionado
    })

def revisar_pedido(request):
    pedido = request.session.get('pedido', {})

    # Se houver parâmetro de edição, remove o campo e redireciona
    campo_editar = request.GET.get('editar')
    if campo_editar in pedido:
        del pedido[campo_editar]
        request.session['pedido'] = pedido

        # Mapeia o campo para a view de seleção correspondente
        etapas = {
            'tamanho': 'pedido:selecionar_tamanho',
            'sabores': 'pedido:selecionar_sabores',
            'pagamento': 'pedido:selecionar_pagamento',
            'endereco': 'pedido:selecionar_endereco'
        }

        return redirect(etapas.get(campo_editar, 'pedido:revisar_pedido'))

    # Verifica se todas as etapas foram preenchidas
    if not all(key in pedido for key in ('tamanho', 'sabores', 'pagamento', 'endereco')):
        return redirect('pedido:selecionar_tamanho')

    if request.method == "POST":
        # Finaliza o pedido e limpa a sessão
        request.session.flush()
        return render(request, 'pedido/finalizado.html', {'pedido': pedido, 'etapa': 'finalizado'})

    return render(request, 'pedido/revisao.html', {'pedido': pedido, 'etapa': 'revisao'})
