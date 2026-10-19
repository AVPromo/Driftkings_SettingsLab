# Etapa 4 — validar ícones e escala no Gameface real

## Âmbito desta build

O painel diagnóstico ganhou uma grelha de amostras fixas, sem posições ou dados de combate. Não cria outro minimapa. Os sete símbolos são LT, MT, HT, TD, SPG, TU (jogador) e X (destruído), em três tamanhos lógicos: 16, 24 e 32 px. As cores são amostras fixas, não uma configuração nova de produção.

A implementação de glifos/renderer sintético foi movida de `prototypes/tactical_minimap/renderer.js` para a biblioteca partilhada `mod/res/gui/gameface/mods/Driftkings/TacticalMinimap/graphics.js`. O preview HTML usa agora o mesmo código. O renderer continua a aceitar apenas fixtures sintéticas; o diagnóstico chama somente `createGlyph`, não renderiza marcadores de batalha.

Os SVG de referência continuam fora do WOTMOD. Um teste compara os caminhos desses sete SVG com os glifos partilhados, incluindo a faixa do MT. A biblioteca partilhada está declarada no manifesto e é carregada antes do script diagnóstico pelo catálogo existente.

## Procedimento

1. Com o jogo fechado, instalar o WOTMOD debug recompilado em `mods/2.4.1.0/Driftkings.wotmod`.
2. Manter `tacticalDiagnostics: true` no `minimap.json` do perfil ativo, como no teste anterior. Reiniciar o cliente.
3. Abrir o mesmo replay NA já utilizado para facilitar a comparação. O diagnóstico deverá mostrar os símbolos, os tamanhos e o estado do SVG DOM.
4. Confirmar visualmente: todos os sete símbolos aparecem; MT tem uma faixa e HT duas; TD é triangular; SPG é circular; o jogador tem um chevron; destruído tem uma cruz; as cores e os três tamanhos são distintos.
5. Confirmar que o minimapa normal, TAB, ocultação do HUD, entrada/saída e reabertura do replay continuam funcionais. Testar resoluções/DPI diferentes antes de aprovar a biblioteca para o renderer.
6. Se nada for desenhado, registar o texto exato e recolher game.log. O modo nativo deve continuar disponível. Para desligar o diagnóstico, repor a flag em false e reiniciar.

O WOTMOD local está em `build/debug/beta/0.1.2-beta.4/Driftkings.wotmod`. Não foi instalado automaticamente.

## Interpretação do log

Após o handshake, o logger `Driftkings.TacticalMinimapProbe` regista:

`Graphics diagnostic: SVG DOM=True glyph nodes=21/21; visual confirmation required`

Isto significa que a API aceitou a criação dos elementos SVG/path. **Não prova que o compositor os desenhou corretamente.** A aprovação visual continua a ser necessária. False/0 indica que o script diagnóstico não conseguiu usar a biblioteca/API; a grelha é omitida e o texto continua. Se o próprio asset JavaScript não carregar, o bootstrap pode interromper todo o diagnóstico; o minimapa nativo continua intacto e o erro deve ser recolhido no log.

O relatório é limitado a um booleano e uma contagem inteira de 0 a 21, associado à geração atual da batalha. Não ativa o modo Driftkings nem Lost Contact. Não há novas subscrições, hooks, comandos de jogo ou timers nesta etapa. A API é sondada dentro de try/catch; um erro na criação SVG não é propagado para o resto do HUD.

## Verificação local

- 60 testes Core em Python 2.7 e 3, incluindo limites do relatório gráfico, geração e limpeza.
- Testes Node: SVGs de referência, geometrias/cores/tamanhos, API em falta ou que lança erro, ausência de reconstrução gráfica em atualizações de metadados e remoção de DOM/callbacks.
- Lint ES5, validação de build e recursos pelo catálogo existente.
- Sem validação visual desta grelha dentro do jogo nesta sessão. Sem medições de FPS ou memória gráfica.

Após confirmação visual, a próxima fase será ligar um renderer cartográfico controlado aos contratos nativos, ainda com o gate de substituição condicionado à paridade de input e fallback. A ponte parcial atual continua insuficiente para substituir o minimapa.
