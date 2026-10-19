# Troca segura Vanilla / Driftkings

## Estado após os testes NA

A amostra continua ao lado do original. O utilizador confirmou a recuperação da seta própria ao alternar para sniper. A roda do rato foi retirada a pedido do utilizador; não faz parte do redimensionamento pretendido. O tamanho continua a acompanhar as teclas nativas, quando essa preferência está ativa, ou o tamanho fixo configurado.

## Próxima implementação: ocultar a apresentação sem perder os contratos

Não usar simplesmente `as_setVisibleS(false)` ou alpha zero no componente completo. Os leitores atuais de pings de célula e área estratégica verificam `minimap.visible` e `minimap.alpha`; ocultá-lo desta forma pode eliminar os dados necessários ao novo mapa. Também é necessário preservar os handlers nativos de input, os plugins e as atualizações C++/Flash. Ainda não existe um contrato verificado para ocultar exclusivamente a apresentação preservando estas funções.

A primeira entrega desta fase deve, por isso, auditar a árvore e as superfícies gráficas do Flash real, identificar quais podem ser ocultadas e guardar os valores exatos a restaurar. A alteração só pode ser aplicada ao componente proprietário dessa batalha, nunca globalmente aos outros mapas ou às preferências do jogo. Se a superfície não puder ser separada com segurança, a substituição permanece indisponível.

## Sondagem estrutural implementada

O método Flash `as_DriftkingsPresentationAudit`, registado em BaseMinimap pela biblioteca compilada, lê apenas metadados. Identifica `background`, `entriesContainer` e `mapHit` por referência, assinala se a área de input está contida nas superfícies gráficas e enumera até 32 ramos diretos. Não chama setters, não move objetos nem muda alpha, visible, mouseEnabled ou mouseChildren. A geometria continua pela via existente.

O parser Python valida comprimento, contagens, flags, alfa e nomes/classes antes de registar no log. O resultado nunca permite a substituição (`replacementAllowed=false`), mesmo quando há separação estrutural. Uma superfície separada na árvore não prova que ocultá-la preserve o desenho C++/Flash ou todas as interações. Métodos ausentes ou respostas inválidas não impedem o diagnóstico normal do mapa.

A leitura é feita uma vez quando a geometria fica disponível, por ligação ao componente; não acrescenta timer ou hook. O log contém `Native presentation audit` e `Native presentation branch`. Roles é uma máscara: 1=fundo, 2=entradas, 4=área de input; um ramo com 3 ou 6 contém mais de uma destas funções. Só guarda nomes/classes de superfícies da interface, sem IDs ou posições de veículos.

Para recolher: instalar o pacote recompilado, reiniciar o jogo, entrar numa missão Topography e voltar ao hangar. Consultar o log e comparar com a árvore auditada do SRC/SWF. A confirmação seguinte é estrutural; não se espera mudança visual nesta entrega. A ocultação e a recuperação independente continuam por implementar.

## Resultado do ensaio por scrollRect — via retirada

No ensaio NA/Topography de 2026-10-19, o log registou início às 20:14:46.786 e reposição às 20:14:49.726. A captura enviada pelo utilizador às 20:15:01 mostra o fundo original vermelho e círculos/linhas fora da área do mapa. A reposição das propriedades Flash não demonstrou reposição correta do desenho nativo.

A implementação de recorte por scrollRect foi retirada por completo: helper Flash, comando, controlo, flag nos defaults e arranque Python. Um valor antigo `tacticalPresentationTrial=true` nas configurações fica sem consumidor e não pode ativar o ensaio na build corrigida. A sondagem estrutural só de leitura mantém-se.

Este resultado invalida esta implementação de ocultação. Não se repete nem se ativa como troca permanente. A hipótese de que os ramos separados na árvore poderiam ser recortados preservando a apresentação C++ não ficou comprovada. Uma alternativa precisa de auditoria das superfícies C++/Flash e nova prova de reposição, antes de qualquer ocultação. A substituição permanece bloqueada.

Após instalar o pacote corrigido é necessário reiniciar o cliente para recriar as superfícies nativas; remover a opção ou restaurar propriedades em memória não prova que uma superfície já afetada fique recuperada. Confirmar que o original regressa normal, sem vermelho ou linhas a sair do mapa.

## Condições para assumir a apresentação

- Escolha Driftkings guardada antes do início da batalha, sem troca durante combate nesta primeira versão.
- Componente e modo auditados, sem proprietário incompatível ou XVM.
- Geometria válida, textura disponível, handshake da geração atual e primeiro frame completo efetivamente apresentado.
- Paridade dos elementos essenciais confirmada, incluindo os testes de artilharia pendentes e a interação original.
- Recuperação independente do JavaScript: se o Gameface parar, a apresentação nativa deve regressar sem depender de um callback do próprio Gameface.

A flag `PRODUCTION_REPLACEMENT_VERIFIED` permanece falsa. Uma preferência guardada ou um handshake de diagnóstico não permitem ultrapassar estes critérios.

## Recuperação a comprovar antes de ativar

O mecanismo que oculta a apresentação deve possuir uma autorização com prazo curto, renovada apenas após confirmação de apresentação do Gameface. O relógio e a reposição têm de existir na camada nativa/Flash, independentemente da vista Gameface. Gerações antigas, mensagens atrasadas e renovação após destruição devem ser recusadas. A reposição restaura os valores guardados, sem forçar visibilidade se o jogador tiver ocultado o HUD.

Testar falha de carregamento, falha de desenho, ausência de confirmações, perda da vista, mudança de resolução, HUD oculto, saída de batalha e troca de componente. Em cada caso, confirmar ausência de duplicações e que o original permanece ou regressa utilizável. Não ativar a substituição com base apenas em mocks.

## O que esta etapa não comprova

Ainda não há ocultação nem lease nativo implementados. Os testes existentes cobrem a amostra e a política bloqueada. A seleção específica de veículos continua sem contrato confirmado; não será inventada nem convertida silenciosamente em ping de posição. Compatibilidade EU/NA/ASIA não pode ser deduzida apenas do SRC EU ou dos testes NA/Topography.
