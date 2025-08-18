// Variáveis globais para armazenar o pedido
const pedido = {
    tamanho: null,
    sabores: [],
    pagamento: null,
    nome: '',
    telefone: '',
    endereco: '',
    retirada: false
};

// Elementos do DOM
const secoes = {
    tamanho: document.getElementById('secaoTamanho'),
    sabores: document.getElementById('secaoSabores'),
    pagamento: document.getElementById('secaoPagamento'),
    endereco: document.getElementById('secaoEndereco')
};

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
    finalizar: document.getElementById('botaoFinalizar')
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
            pedido.tamanho = radio.value;
        } else {
            card.classList.remove('selecionado');
        }
    });

    // Atualizar sabores
    document.querySelectorAll('input[name="sabor"]').forEach(checkbox => {
        const card = checkbox.closest('.cartao-sabor');
        if (checkbox.checked) {
            card.classList.add('selecionado');
            if (!pedido.sabores.includes(checkbox.value)) {
                pedido.sabores.push(checkbox.value);
            }
        } else {
            card.classList.remove('selecionado');
            const indice = pedido.sabores.indexOf(checkbox.value);
            if (indice > -1) {
                pedido.sabores.splice(indice, 1);
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
document.querySelectorAll('input[name="sabor"]').forEach(checkbox => {
    checkbox.addEventListener('change', atualizarVisualizacaoSelecao);
});

// Ouvintes de eventos para pagamento
document.querySelectorAll('input[name="pagamento"]').forEach(radio => {
    radio.addEventListener('change', atualizarVisualizacaoSelecao);
});

// Adicionar eventos de clique nos labels para melhor UX
document.querySelectorAll('.cartao-opcao label, .cartao-sabor label').forEach(label => {
    label.addEventListener('click', function(e) {
        // Permitir que o clique no label marque o input correspondente
        const input = this.querySelector('input') || this.previousElementSibling;
        if (input && input.type === 'radio') {
            input.checked = true;
        } else if (input && input.type === 'checkbox') {
            input.checked = !input.checked;
        }
        atualizarVisualizacaoSelecao();
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
}

// Função para atualizar o resumo
function atualizarResumo() {
    elementosResumo.tamanho.textContent = `Tamanho: ${pedido.tamanho}`;
    elementosResumo.sabores.textContent = `Sabores: ${pedido.sabores.join(', ')}`;
    elementosResumo.pagamento.textContent = `Pagamento: ${pedido.pagamento}`;
    
    if (pedido.retirada) {
        elementosResumo.entrega.textContent = `Entregar?: Não, vou retirar no balcão`;
    } else {
        elementosResumo.entrega.textContent = `Endereço: ${pedido.endereco}`;
    }
    
    resumoPedido.classList.remove('oculto');
}

// Ouvintes de eventos para os botões
botoes.proximo1.addEventListener('click', function() {
    if (!pedido.tamanho) {
        mostrarErro('Por favor, selecione um tamanho para sua pizza.');
        return;
    }
    
    mudarSecao(secoes.tamanho, secoes.sabores);
    etapas.etapa1.classList.remove('active');
    etapas.etapa1.classList.add('completed');
    etapas.etapa2.classList.add('active');
});

botoes.proximo2.addEventListener('click', function() {
    if (pedido.sabores.length === 0) {
        mostrarErro('Por favor, selecione pelo menos um sabor.');
        return;
    }
    
    // Verifica se o número de sabores é válido para o tamanho
    if ((pedido.tamanho === 'Pequena' || pedido.tamanho === 'Média') && pedido.sabores.length > 1) {
        mostrarErro(`Pizza ${pedido.tamanho} só pode ter um sabor.`);
        return;
    }
    
    if (pedido.tamanho === 'Grande' && pedido.sabores.length > 2) {
        mostrarErro('Pizza Grande pode ter no máximo 2 sabores.');
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
    
    // Construir mensagem para WhatsApp
    let mensagem = `*NOVO PEDIDO - PIZZARIA DELÍCIA*%0A%0A`;
    mensagem += `*Nome:* ${pedido.nome}%0A`;
    mensagem += `*Telefone:* ${pedido.telefone}%0A`;
    mensagem += `*Tamanho:* ${pedido.tamanho}%0A`;
    mensagem += `*Sabores:* ${pedido.sabores.join(', ')}%0A`;
    mensagem += `*Forma de pagamento:* ${pedido.pagamento}%0A`;
    mensagem += `*Entrega:* ${pedido.retirada ? 'Retirada no balcão' : pedido.endereco}%0A%0A`;
    mensagem += `*Obrigado pelo pedido!*`;
    
    // Redirecionar para WhatsApp (substitua o número pelo real)
    window.location.href = `https://wa.me/5511999999999?text=${mensagem}`;
});
