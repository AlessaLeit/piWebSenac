// Variáveis globais para armazenar o pedido
const pedido = {
    pizzas: [],
    pagamento: null,
    nome: '',
    telefone: '',
    endereco: '',
    retirada: false
};

let pizzaAtual = {
    tamanho: null,
    sabores: []
};

// Elementos do DOM
const secoes = {
    tamanho: document.getElementById('secaoTamanho'),
    sabores: document.getElementById('secaoSabores'),
    pagamento: document.getElementById('secaoPagamento'),
    endereco: document.getElementById('secaoEndereco'),
    revisao: document.getElementById('secaoRevisao'),
    edicao: document.getElementById('secaoEdicao')
};

// Botões de revisão
const botaoConfirmar = document.getElementById('botaoConfirmar');
const botaoEditar = document.getElementById('botaoEditar');
const resumoDetalhado = document.getElementById('resumoDetalhado');

const etapas = {
    etapa1: document.getElementById('step1'),
    etapa2: document.getElementById('step2'),
    etapa3: document.getElementById('step3'),
    etapa4: document.getElementById('step4')
};

const botoes = {
    proximo1: document.getElementById('botaoProximo1'),
    proximo2: document.getElementById('botaoProximo2'),
    proximo3: document.getElementById('botaoProximo3'),
    voltar1: document.getElementById('botaoVoltar1'),
    voltar2: document.getElementById('botaoVoltar2'),
    voltar3: document.getElementById('botaoVoltar3'),
    finalizar: document.getElementById('botaoFinalizar'),
    adicionar: document.getElementById('botaoAdicionar')
};

const alertaErro = document.getElementById('alertaErro');
const checkboxRetirada = document.getElementById('retirada');
const camposEndereco = document.getElementById('camposEndereco');
const resumoPedido = document.getElementById('resumoPedido');
const elementosResumo = {
    tamanho: document.getElementById('resumoTamanho'),
    sabores: document.getElementById('resumoSabores'),
    pagamento: document.getElementById('resumoPagamento'),
    entrega: document.getElementById('resumoEntrega')
};

// Função para atualizar visualização de seleção
function atualizarVisualizacaoSelecao() {
    // Atualizar tamanhos
    document.querySelectorAll('input[name="tamanho"]').forEach(radio => {
        const card = radio.closest('.cartao-opcao');
        if (radio.checked) {
            card.classList.add('selecionado');
            pizzaAtual.tamanho = radio.value;
        } else {
            card.classList.remove('selecionado');
        }
    });

    // Atualizar sabores
    document.querySelectorAll('input[name="sabor[]"]').forEach(checkbox => {
        const card = checkbox.closest('.cartao-sabor');
        if (checkbox.checked) {
            card.classList.add('selecionado');
            if (!pizzaAtual.sabores.includes(checkbox.value)) {
                pizzaAtual.sabores.push(checkbox.value);
            }
        } else {
            card.classList.remove('selecionado');
            const indice = pizzaAtual.sabores.indexOf(checkbox.value);
            if (indice > -1) {
                pizzaAtual.sabores.splice(indice, 1);
            }
        }
    });

    // Atualizar pagamento
    document.querySelectorAll('input[name="pagamento"]').forEach(radio => {
        const card = radio.closest('.cartao-opcao');
        if (radio.checked) {
            card.classList.add('selecionado');
            pedido.pagamento = radio.value;
        } else {
            card.classList.remove('selecionado');
        }
    });
}

// Ouvintes de eventos para os tamanhos
document.querySelectorAll('input[name="tamanho"]').forEach(radio => {
    radio.addEventListener('change', atualizarVisualizacaoSelecao);
});

// Ouvintes de eventos para os sabores
document.querySelectorAll('input[name="sabor[]"]').forEach(checkbox => {
    checkbox.addEventListener('change', atualizarVisualizacaoSelecao);
});

// Ouvintes de eventos para pagamento
document.querySelectorAll('input[name="pagamento"]').forEach(radio => {
    radio.addEventListener('change', atualizarVisualizacaoSelecao);
});

// Adicionar eventos de clique nos labels para melhor UX
document.querySelectorAll('.cartao-opcao label, .cartao-sabor label').forEach(label => {
    label.addEventListener('click', function(e) {
        // Impedir a propagação do evento para evitar múltiplos cliques
        e.stopPropagation();
        
        // Encontrar o input correspondente de forma mais robusta
        let input;
        const inputId = this.getAttribute('for');
        
        if (inputId) {
            // Se o label tem atributo 'for', buscar the input pelo ID
            input = document.getElementById(inputId);
        } else {
            // Se não tem atributo 'for', procurar input dentro do label
            input = this.querySelector('input');
        }
        
        if (input && input.type === 'radio') {
            input.checked = true;
            atualizarVisualizacaoSelecao();
        } else if (input && input.type === 'checkbox') {
            // Para checkboxes, alternar o estado
            input.checked = !input.checked;
            
            // Disparar o evento change manualmente para atualizar a visualização
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        }
    });
});

// Adicionar evento de clique direto nos cartões de sabor para melhor UX
document.querySelectorAll('.cartao-sabor').forEach(cartao => {
    cartao.addEventListener('click', function(e) {
        // Evitar que o clique no checkbox ou label dispare duplamente
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') {
            const checkbox = this.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                const event = new Event('change', { bubbles: true });
                checkbox.dispatchEvent(event);
            }
        }
    });
});

// Inicializar visualização
document.addEventListener('DOMContentLoaded', function() {
    atualizarVisualizacaoSelecao();
    etapas.etapa1.classList.add('active');
});

// Ouvinte para retirada no balcão
checkboxRetirada.addEventListener('change', function() {
    pedido.retirada = this.checked;
    camposEndereco.style.display = this.checked ? 'none' : 'block';
});

// Função para mostrar erro
function mostrarErro(mensagem) {
    alertaErro.textContent = mensagem;
    alertaErro.style.display = 'block';
    setTimeout(() => {
        alertaErro.style.display = 'none';
    }, 5000);
}

// Função para mudar de seção
function mudarSecao(de, para) {
    de.classList.add('oculto');
    para.classList.remove('oculto');
    
    // Quando a seção de sabores é mostrada, restaurar os estados dos checkboxes
    if (para.id === 'secaoSabores') {
        restaurarSelecaoSabores();
    }
}

// Função para restaurar a seleção dos sabores
function restaurarSelecaoSabores() {
    document.querySelectorAll('input[name="sabor[]"]').forEach(checkbox => {
        // Restaurar o estado checked baseado no array pizzaAtual.sabores
        checkbox.checked = pizzaAtual.sabores.includes(checkbox.value);
        
        // Atualizar a visualização do cartão
        const card = checkbox.closest('.cartao-sabor');
        if (checkbox.checked) {
            card.classList.add('selecionado');
        } else {
            card.classList.remove('selecionado');
        }
    });
}

// Função para atualizar o resumo
function atualizarResumo() {
    // Limpar resumo anterior
    elementosResumo.tamanho.innerHTML = '';
    elementosResumo.sabores.innerHTML = '';
    
    // Adicionar cada pizza ao resumo
    pedido.pizzas.forEach((pizza, index) => {
        const pizzaNum = index + 1;
        const tamanhoItem = document.createElement('div');
        if (tamanhoItem === 'Calzone') {
            tamanhoItem.textContent = `Item ${pizzaNum}: Tamanho - ${pizza.tamanho}`;
        }
        else { 
            tamanhoItem.textContent = `Item ${pizzaNum}: Tamanho - Pizza ${pizza.tamanho}`;
        }
        elementosResumo.tamanho.appendChild(tamanhoItem);
        
        const saboresItem = document.createElement('div');
        saboresItem.textContent = `Item ${pizzaNum}: Sabores - ${pizza.sabores.join(', ')}`;
        elementosResumo.sabores.appendChild(saboresItem);
    });
    
    elementosResumo.pagamento.textContent = `Pagamento: ${pedido.pagamento}`;
    
    if (pedido.retirada) {
        elementosResumo.entrega.textContent = `Entregar?: Não, vou retirar no balcão`;
    } else {
        elementosResumo.entrega.textContent = `Endereço: ${pedido.endereco}`;
    }
    
    resumoPedido.classList.remove('active');
}

// Função para adicionar pizza atual ao pedido
function adicionarPizzaAoPedido() {
    if (!pizzaAtual.tamanho || pizzaAtual.sabores.length === 0) {
        mostrarErro('Por favor, selecione um tamanho e pelo menos um sabor para a pizza.');
        return false;
    }
    
    // Verifica se o número de sabores é válido para o tamanho
    if (pizzaAtual.tamanho === 'Calzone' && pizzaAtual.sabores.length > 1) {
        mostrarErro('Calzone só pode ter um sabor.');
        return false;
    }
    else if ((pizzaAtual.tamanho === 'Media' || pizzaAtual.tamanho === 'Grande' || pizzaAtual.tamanho === 'Big') && pizzaAtual.sabores.length > 3) {
        mostrarErro('Pizzas podem ter no máximo 3 sabores.');
        return false;
    }
    
    // Adiciona a pizza atual ao pedido
    pedido.pizzas.push({...pizzaAtual});
    
    // Limpa a pizza atual para a próxima seleção
    pizzaAtual = {
        tamanho: null,
        sabores: []
    };
    
    // Limpa a seleção visual
    document.querySelectorAll('input[name="tamanho"]').forEach(radio => {
        radio.checked = false;
        radio.closest('.cartao-opcao').classList.remove('selecionado');
    });
    
    document.querySelectorAll('input[name="sabor[]"]').forEach(checkbox => {
        checkbox.checked = false;
        checkbox.closest('.cartao-sabor').classList.remove('selecionado');
    });
    
    return true;
}

// Ouvintes de eventos para os botões
botoes.proximo1.addEventListener('click', function() {
    if (!pizzaAtual.tamanho) {
        mostrarErro('Por favor, selecione um tamanho para sua pizza.');
        return;
    }
    
    mudarSecao(secoes.tamanho, secoes.sabores);
    etapas.etapa1.classList.remove('active');
    etapas.etapa1.classList.add('completed');
    etapas.etapa2.classList.add('active');
});


botoes.proximo2.addEventListener('click', function() {
    if (pizzaAtual.sabores.length === 0) {
        mostrarErro('Por favor, selecione pelo menos um sabor.');
        return;
    }
    
    // Verifica se o número de sabores é válido para o tamanho
    if (pizzaAtual.tamanho === 'Calzone' && pizzaAtual.sabores.length > 1) {
        mostrarErro('Calzone só pode ter um sabor.');
        return;
    }
    else if ((pizzaAtual.tamanho === 'Media' || pizzaAtual.tamanho === 'Grande' || pizzaAtual.tamanho === 'Big') && pizzaAtual.sabores.length > 3) {
        mostrarErro('Pizzas podem ter no máximo 3 sabores.');
        return;
    }
    
    // Adiciona a pizza atual ao pedido antes de prosseguir
    if (!adicionarPizzaAoPedido()) {
        return;
    }
    
    mudarSecao(secoes.sabores, secoes.pagamento);
    etapas.etapa2.classList.remove('active');
    etapas.etapa2.classList.add('completed');
    etapas.etapa3.classList.add('active');
});

botoes.proximo3.addEventListener('click', function() {
    if (!pedido.pagamento) {
        mostrarErro('Por favor, selecione uma forma de pagamento.');
        return;
    }
    
    mudarSecao(secoes.pagamento, secoes.endereco);
    etapas.etapa3.classList.remove('active');
    etapas.etapa3.classList.add('completed');
    etapas.etapa4.classList.add('active');
});

botoes.voltar1.addEventListener('click', function() {
    mudarSecao(secoes.sabores, secoes.tamanho);
    etapas.etapa2.classList.remove('active');
    etapas.etapa1.classList.add('active');
});

botoes.voltar2.addEventListener('click', function() {
    mudarSecao(secoes.pagamento, secoes.sabores);
    etapas.etapa3.classList.remove('active');
    etapas.etapa2.classList.add('active');
});

botoes.voltar3.addEventListener('click', function() {
    mudarSecao(secoes.endereco, secoes.pagamento);
    etapas.etapa4.classList.remove('active');
    etapas.etapa3.classList.add('active');
    resumoPedido.classList.add('oculto');
});

botoes.finalizar.addEventListener('click', function() { 
    // Validar dados
    pedido.nome = document.getElementById('nome').value.trim();
    pedido.telefone = document.getElementById('telefone').value.trim();
    
    if (!pedido.retirada) {
        pedido.endereco = document.getElementById('endereco').value.trim();
        if (!pedido.endereco) {
            mostrarErro('Por favor, informe o endereço de entrega.');
            return;
        }
    } else {
        pedido.endereco = 'Retirada no balcão';
    }
    
    if (!pedido.nome) {
        mostrarErro('Por favor, informe seu nome.');
        return;
    }
    
    if (!pedido.telefone) {
        mostrarErro('Por favor, informe seu telefone.');
        return;
    }
    
    // Atualizar resumo
    atualizarResumo();
    
    // Mostrar seção de revisão em vez de enviar diretamente
    mostrarRevisaoPedido();
});

// Função para mostrar a revisão do pedido
function mostrarRevisaoPedido() {
    // Limpar resumo anterior
    resumoDetalhado.innerHTML = '';
    
    // Adicionar informações do pedido ao resumo detalhado
    const infoCliente = document.createElement('p');
    infoCliente.innerHTML = `<strong>Cliente:</strong> ${pedido.nome}<br><strong>Telefone:</strong> ${pedido.telefone}`;
    resumoDetalhado.appendChild(infoCliente);
    
    // Adicionar cada pizza ao resumo
    pedido.pizzas.forEach((pizza, index) => {
        const pizzaNum = index + 1;
        const pizzaInfo = document.createElement('p');
        pizzaInfo.innerHTML = `<strong>Item ${pizzaNum}:</strong><br>
                              <strong>Tamanho:</strong> ${pizza.tamanho}<br>
                              <strong>Sabores:</strong> ${pizza.sabores.join(', ')}`;
        resumoDetalhado.appendChild(pizzaInfo);
    });
    
    // Adicionar forma de pagamento
    const pagamentoInfo = document.createElement('p');
    pagamentoInfo.innerHTML = `<strong>Forma de pagamento:</strong> ${pedido.pagamento}`;
    resumoDetalhado.appendChild(pagamentoInfo);
    
    // Adicionar informações de entrega
    const entregaInfo = document.createElement('p');
    entregaInfo.innerHTML = `<strong>Entrega:</strong> ${pedido.retirada ? 'Retirada no balcão' : pedido.endereco}`;
    resumoDetalhado.appendChild(entregaInfo);
    
    // Mostrar seção de revisão e esconder seção de endereço
    mudarSecao(secoes.endereco, secoes.revisao);
}

// Função para enviar pedido para WhatsApp
function enviarParaWhatsApp() {
    // Construir mensagem para WhatsApp
    let mensagem = `*NOVO PEDIDO - CASA DAS PIZZAS*`; 
    mensagem += `\n*Nome:* ${pedido.nome}`;
    mensagem += `\n*Telefone:* ${pedido.telefone}`;
    
    // Adicionar cada pizza à mensagem
    pedido.pizzas.forEach((pizza, index) => {
        const pizzaNum = index + 1;
        mensagem += `\n*Pizza ${pizzaNum}:*`;
        mensagem += `\n  *Tamanho:* ${pizza.tamanho}`;
        mensagem += `\n  *Sabores:* ${pizza.sabores.join(', ')}`;
    });
    
    mensagem += `\n*Forma de pagamento:* ${pedido.pagamento}`;
    mensagem += `\n*Entrega:* ${pedido.retirada ? 'Retirada no balcão' : pedido.endereco}`;
    mensagem += `\n*Obrigado pelo pedido!*`;

    // Redirecionar para WhatsApp (substitua o número pelo real)
    window.location.href = `https://wa.me/5511999999999?text=${encodeURIComponent(mensagem)}`;
}

// Função para voltar para edição do pedido
function voltarParaEdicao() {
    mudarSecao(secoes.revisao, secoes.endereco);
}

// Variável para controlar qual pizza está sendo editada
let pizzaEditandoIndex = null;

// Função para mostrar botões de edição/exclusão para cada pizza
function mostrarBotoesEdicao() {
    // Limpar resumo anterior
    resumoDetalhado.innerHTML = '';
    
    // Adicionar informações do pedido ao resumo detalhado
    const infoCliente = document.createElement('p');
    infoCliente.innerHTML = `<strong>Cliente:</strong> ${pedido.nome}<br><strong>Telefone:</strong> ${pedido.telefone}`;
    resumoDetalhado.appendChild(infoCliente);
    
    // Adicionar cada pizza ao resumo com botões de editar/excluir
    pedido.pizzas.forEach((pizza, index) => {
        const pizzaNum = index + 1;
        const pizzaContainer = document.createElement('div');
        pizzaContainer.className = 'pizza-item';
        pizzaContainer.innerHTML = `
            <p><strong>Item ${pizzaNum}:</strong><br>
            <strong>Tamanho:</strong> ${pizza.tamanho}<br>
            <strong>Sabores:</strong> ${pizza.sabores.join(', ')}</p>
            <div class="botoes-pizza">
                <button class="botao botao-editar-pizza" data-index="${index}">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button class="botao botao-excluir-pizza" data-index="${index}">
                    <i class="fas fa-trash"></i> Excluir
                </button>
            </div>
        `;
        resumoDetalhado.appendChild(pizzaContainer);
    });
    
    // Adicionar forma de pagamento
    const pagamentoInfo = document.createElement('p');
    pagamentoInfo.innerHTML = `<strong>Forma de pagamento:</strong> ${pedido.pagamento}`;
    resumoDetalhado.appendChild(pagamentoInfo);
    
    // Adicionar informações de entrega
    const entregaInfo = document.createElement('p');
    entregaInfo.innerHTML = `<strong>Entrega:</strong> ${pedido.retirada ? 'Retirada no balcão' : pedido.endereco}`;
    resumoDetalhado.appendChild(entregaInfo);
    
    // Adicionar event listeners para os botões de editar/excluir
    document.querySelectorAll('.botao-editar-pizza').forEach(botao => {
        botao.addEventListener('click', function() {
            const index = parseInt(this.getAttribute('data-index'));
            editarPizza(index);
        });
    });
    
    document.querySelectorAll('.botao-excluir-pizza').forEach(botao => {
        botao.addEventListener('click', function() {
            const index = parseInt(this.getAttribute('data-index'));
            excluirPizza(index);
        });
    });
}

// Função para editar uma pizza específica
function editarPizza(index) {
    pizzaEditandoIndex = index;
    const pizza = pedido.pizzas[index];
    
    // Preencher a pizza atual com os dados da pizza sendo editada
    pizzaAtual = {...pizza};
    
    // Mostrar seção de edição
    mudarSecao(secoes.revisao, secoes.edicao);
    
    // Criar conteúdo de edição
    const conteudoEdicao = document.getElementById('conteudoEdicao');
    conteudoEdicao.innerHTML = `
        <h3>Editando Pizza ${index + 1}</h3>
        <div class="grade-opcoes">
            ${['Media', 'Grande', 'Big', 'Calzone'].map(tamanho => `
                <div class="cartao-opcao ${pizzaAtual.tamanho === tamanho ? 'selecionado' : ''}">
                    <input type="radio" id="edit-${tamanho.toLowerCase()}" name="edit-tamanho" value="${tamanho}" ${pizzaAtual.tamanho === tamanho ? 'checked' : ''}>
                    <label for="edit-${tamanho.toLowerCase()}">
                        <span>${tamanho === 'Calzone' ? 'Calzone' : 'Pizza ' + tamanho}</span>
                        <span class="preco">R$ 99,00</span>
                    </label>
                </div>
            `).join('')}
        </div>
        
        <h3 style="margin-top: 20px;">Escolha os sabores</h3>
        <div class="grade-sabores">
            ${['Margherita', 'Calabresa', 'Portuguesa', 'Frango Catupiry', 'Quatro Queijos', 'Pepperoni'].map(sabor => `
                <div class="cartao-sabor ${pizzaAtual.sabores.includes(sabor) ? 'selecionado' : ''}">
                    <label for="edit-${sabor.toLowerCase().replace(' ', '-')}">
                        <input type="checkbox" id="edit-${sabor.toLowerCase().replace(' ', '-')}" name="edit-sabor[]" value="${sabor}" ${pizzaAtual.sabores.includes(sabor) ? 'checked' : ''}>
                        <div class="info-sabor">
                            <h3>${sabor}</h3>
                            <p>${getSaborDescription(sabor)}</p>
                        </div>
                    </label>
                </div>
            `).join('')}
        </div>
    `;
    
    // Atualizar visualização de seleção
    atualizarVisualizacaoSelecao();
    
    // Adicionar event listeners para os inputs de edição
    document.querySelectorAll('input[name="edit-tamanho"]').forEach(radio => {
        radio.addEventListener('change', function() {
            pizzaAtual.tamanho = this.value;
            atualizarVisualizacaoSelecao();
        });
    });
    
    document.querySelectorAll('input[name="edit-sabor[]"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                if (!pizzaAtual.sabores.includes(this.value)) {
                    pizzaAtual.sabores.push(this.value);
                }
            } else {
                const indice = pizzaAtual.sabores.indexOf(this.value);
                if (indice > -1) {
                    pizzaAtual.sabores.splice(indice, 1);
                }
            }
            atualizarVisualizacaoSelecao();
        });
    });
}

// Função auxiliar para obter descrição do sabor
function getSaborDescription(sabor) {
    const descricoes = {
        'Margherita': 'Molho, mussarela, tomate e manjericão',
        'Calabresa': 'Molho, mussarela e calabresa fatiada',
        'Portuguesa': 'Molho, mussarela, presunto, ovo e azeitonas',
        'Frango Catupiry': 'Molho, mussarela, frango desfiado e catupiry',
        'Quatro Queijos': 'Molho, mussarela, gorgonzola, parmesão e provolone',
        'Pepperoni': 'Molho, mussarela e pepperoni'
    };
    return descricoes[sabor] || '';
}

// Função para excluir uma pizza
function excluirPizza(index) {
    if (confirm('Tem certeza que deseja excluir esta pizza?')) {
        pedido.pizzas.splice(index, 1);
        
        // Se não houver mais pizzas, voltar para a seção de tamanho
        if (pedido.pizzas.length === 0) {
            mudarSecao(secoes.revisao, secoes.tamanho);
            etapas.etapa1.classList.add('active');
            etapas.etapa2.classList.remove('active');
            etapas.etapa3.classList.remove('active');
            etapas.etapa4.classList.remove('active');
        } else {
            // Atualizar o resumo
            mostrarBotoesEdicao();
        }
    }
}

// Função para salvar as alterações da pizza editada
function salvarEdicao() {
    if (!pizzaAtual.tamanho || pizzaAtual.sabores.length === 0) {
        mostrarErro('Por favor, selecione um tamanho e pelo menos um sabor para a pizza.');
        return;
    }
    
    // Verifica se o número de sabores é válido para o tamanho
    if (pizzaAtual.tamanho === 'Calzone' && pizzaAtual.sabores.length > 1) {
        mostrarErro('Calzone só pode ter um sabor.');
        return;
    }
    else if ((pizzaAtual.tamanho === 'Media' || pizzaAtual.tamanho === 'Grande' || pizzaAtual.tamanho === 'Big') && pizzaAtual.sabores.length > 3) {
        mostrarErro('Pizzas podem ter no máximo 3 sabores.');
        return;
    }
    
    // Atualizar a pizza no array
    pedido.pizzas[pizzaEditandoIndex] = {...pizzaAtual};
    
    // Limpar a pizza atual
    pizzaAtual = {
        tamanho: null,
        sabores: []
    };
    
    // Voltar para a seção de revisão
    mudarSecao(secoes.edicao, secoes.revisao);
    
    // Atualizar o resumo
    mostrarBotoesEdicao();
}

// Função para cancelar a edição
function cancelarEdicao() {
    // Limpar a pizza atual
    pizzaAtual = {
        tamanho: null,
        sabores: []
    };
    
    // Voltar para a seção de revisão
    mudarSecao(secoes.edicao, secoes.revisao);
    
    // Atualizar o resumo
    mostrarBotoesEdicao();
}

// Modificar a função mostrarRevisaoPedido para usar mostrarBotoesEdicao
function mostrarRevisaoPedido() {
    mostrarBotoesEdicao();
    mudarSecao(secoes.endereco, secoes.revisao);
}

// Adicionar event listeners para os botões de edição
document.getElementById('botaoSalvarEdicao').addEventListener('click', salvarEdicao);
document.getElementById('botaoCancelarEdicao').addEventListener('click', cancelarEdicao);

// Adicionar event listeners para os botões de revisão
botaoConfirmar.addEventListener('click', enviarParaWhatsApp);
botaoEditar.addEventListener('click', voltarParaEdicao);
