[# PiWeb

Sistema de pedidos de pizza online desenvolvido em Django.

## Descrição

Este projeto é uma aplicação web para pedidos de pizza, permitindo aos usuários se cadastrarem, fazerem login e realizarem pedidos personalizados de pizzas, incluindo seleção de tamanho, sabores, observações, forma de pagamento e endereço de entrega. Os pedidos são salvos no banco de dados e enviados via WhatsApp para confirmação.

## Funcionalidades

- **Cadastro e Login de Usuários**: Usuários podem se cadastrar com CPF, telefone, endereço e senha. Login pode ser feito com CPF ou telefone.
- **Seleção de Tamanho**: Escolha entre Média, Grande, Big ou Calzone.
- **Seleção de Sabores**: Para pizzas normais, até 3 sabores; para Calzone, apenas 1 sabor.
- **Observações**: Adicionar observações para cada pizza.
- **Pagamento**: Seleção da forma de pagamento.
- **Endereço**: Informar endereço de entrega ou opção de retirada no balcão.
- **Revisão do Pedido**: Visualizar todas as pizzas do pedido, total e detalhes antes de finalizar.
- **Envio via WhatsApp**: Após finalizar, o pedido é enviado para um número específico via WhatsApp.

## Tecnologias Utilizadas

- **Django**: Framework web principal.
- **SQLite**: Banco de dados padrão.
- **HTML/CSS**: Templates e estilos.
- **Twilio**: Para integração com WhatsApp (importado, mas não usado diretamente no código fornecido).

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/AlessaLeit/piWebSenac.git
   cd PiWeb
   ```

2. Crie um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Execute as migrações:
   ```
   python manage.py migrate
   ```

5. Execute o servidor:
   ```
   python manage.py runserver
   ```

6. Acesse no navegador: `http://localhost:8000`

## Uso

- Acesse a página inicial e será redirecionado para seleção de tamanho.
- Faça login ou cadastre-se se necessário.
- Siga os passos: tamanho -> sabores -> confirmar/adicionar mais -> pagamento -> endereço -> revisão -> finalizar (envia WhatsApp).

## Modelos

- **Usuario**: Modelo de usuário personalizado com CPF, telefone e endereço.
- **Pedido**: Representa um pedido com nome, telefone, endereço, retirada e pagamento.
- **Pizza**: Itens do pedido com tamanho, sabores e observação.

## Correções 

- Corrigir campo de observação ✔️
- Corrigir botão flutuante nos sabores ✔️
- Sistema de pesquisa nos sabores 
- Separação de sabores salgados e doces
- Integração do banco de dados (login e cadastro)


## Futuras Implementações

- Adicional de bordas
- Puxar endereço do cadastro 
- Adicionar automaticamente taxa de entrega conforme bairro 
- Pagamento diretamente pelo site 
](https://github.com/AlessaLeit/piWebSenac.git)
