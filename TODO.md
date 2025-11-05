# TODO: Implementar navegação por teclado com Enter nas páginas de progresso

## Arquivos a editar:
- [ ] pi/templates/pedido/tamanho.html
- [ ] pi/templates/pedido/sabores.html
- [ ] pi/templates/pedido/sabores_calzone.html
- [ ] pi/templates/pedido/confirmar_adicionar.html
- [ ] pi/templates/pedido/pagamento.html
- [ ] pi/templates/pedido/endereco.html
- [ ] pi/templates/pedido/revisao.html

## Mudanças necessárias:
- Adicionar tabindex="0" aos steps que têm onclick mas não têm tabindex.
- Adicionar script para navegação por teclado: event listener para keydown Enter nos steps, chamando navegarParaEtapa com o mapeamento correto.

## Mapeamento step id para etapa:
- step1: 'tamanho'
- step2: 'sabores' (onde aplicável)
- step3: 'confirmar_adicionar'
- step4: 'pagamento'
- step5: 'endereco'
- step6: 'revisao'
