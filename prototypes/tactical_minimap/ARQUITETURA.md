# Arquitetura e próximos contratos

## Estado entregue

`core/tactical_minimap.py` não importa BigWorld, GUI, Wulf, Settings ou eventos. Expõe política de seleção bloqueada, defaults do protótipo, transformação matemática e adapter exclusivo de fixtures sintéticas. Nunca oculta o nativo e não conserva coordenadas. `preview_snapshot()` rejeita fontes de batalha: ainda não existe um adapter de batalha completo. A etapa 2 acrescenta um leitor nativo parcial, não instalado, descrito em CONTRATOS_NATIVOS.md.

`TacticalMinimap/graphics.js` (antes renderer.js) recebe apenas `source=synthetic-preview`, marcadores normalizados, relações e estados explícitos; descarta entradas invisíveis/lost antes de desenhar. Atualiza nós por ID e assinatura, remove nós ausentes, valida cores/tamanhos e torna dispose idempotente. Não tem timer de polling, listeners de batalha ou chamadas Python. O harness `preview.js` liga e desliga os controlos da página.

Os SVG são fontes próprias: LT losango, MT losango com uma faixa, HT com duas, TD triângulo, SPG círculo/cruz, jogador chevron e destruído cruz. A relação equipa/pelotão é codificada por cor, mantendo a silhueta da classe. A orientação demonstrada é só a do chevron do jogador. Não há alegação de compatibilidade SVG com Gameface até teste real.

## Integração futura dentro da arquitetura real

1. Reutilizar a definição `minimap_enhancements`, service/store/loader e os quatro documentos existentes; integrar modo e campos com migração explícita, sem mexer à mão no Python de defaults gerado. Acrescentar os textos aos catálogos pelo fluxo de geração/validação existente.
2. Reutilizar os limites de vida `BattleEvents` e os padrões ViewComponent/RandomHUDView existentes. Não criar outro event bus ou scheduler. Definir ownership único e desligar tudo em ended/finalize.
3. Implementar um adapter de entradas **publicadas pelo minimapa nativo** que abranja veículos, objetivos, círculos, zonas, pings e estados especiais. Sinais de saúde/avistamento não bastam. Nada de pesquisar entidades para completar dados que não foram publicados.
4. Confirmar bounds/texture via métodos nativos, sem lista inventada de caminhos de mapas. Validar a convenção norte/eixo z e escala em mapas assimétricos.
5. Provar preservação de input, foco, cliques, zoom, ocultar HUD e replays. Não ativar um renderer que só desenhe veículos.
6. Só ocultar a apresentação original depois de um handshake completo, com restauração independente caso JS ou Python falhe. A troca inicial deve acontecer no início da batalha, sem hot swap durante combate até prova de segurança.
7. Partilhar um contrato de dados pequeno, limitado a informação autorizada; reconciliar incrementalmente no cliente visual, sem trabalho gráfico intensivo em Python.

Os testes atuais cobrem a política bloqueada, não simulam um handoff real entre Flash e Gameface. Não há código de ocultação do nativo neste protótipo.

## Etapa 3 — ponte diagnóstica opt-in

`views/battle/tactical_minimap_probe.py` liga um ViewComponent ao HUD aleatório, via catálogo e gen_resources existentes, apenas com tacticalDiagnostics=true. Reutiliza HookRegistry, on_event, BattleEvents, hudVisibility e publish_card. `core/tactical_minimap_probe.py` reduz o snapshot a metadados sem IDs/posições. O JS não usa SVG/Canvas: mostra apenas texto e confirma o protocolo por geração. Não se liga o renderer do protótipo a estes dados. Ver TESTE_GAMEFACE.md.

## Etapa 4 — biblioteca de glifos partilhada

A biblioteca gráfica foi movida para a pasta Gameface e declarada no manifesto/catálogo. O preview reutiliza-a, e o diagnóstico usa apenas createGlyph para amostras fixas. O handshake existente transporta opcionalmente svgApi/glyphCount, validados no backend; não foram criados hooks, listeners ou comandos adicionais. A grelha é conservada entre mudanças de metadados e libertada ao ocultar/finalizar o diagnóstico. Não há ligação entre o renderer sintético e os snapshots nativos.

## Calibração de coordenadas — estado atual

O diagnóstico recebeu cartografia original, geometria Flash e contorno Gameface. O utilizador confirmou a textura e o alinhamento dos cantos/centro com redimensionamento. A amostra seguinte transporta apenas x/y de um aliado atualmente publicado, após handshake e com geometria válida, para testar a conversão mundo/mapa. Reutiliza o timer Flash existente de 250 ms; não acrescenta scheduler. As descrições anteriores de transporte sem posições correspondem às etapas iniciais. Não são enviados IDs, nomes, inimigos ou histórico. O renderer sintético permanece isolado e a substituição do minimapa continua bloqueada.

### Revisão após testes NA

Os testes do ponto A ficaram bloqueados em `waiting-geometry`. A implementação atual lê a geometria diretamente do `MinimapComponent.flashObject` através de uma função do protótipo nativo instalada pela biblioteca, independente da nossa view auxiliar. Usa o serviço de callbacks existente com um único token de 250 ms, cancelado no fim da batalha. Não lê posições com o HUD oculto. As referências acima ao timer Flash descrevem a implementação anterior, removida. Testes de integração simulados cobrem leitura sem view auxiliar, falha/recuperação, ocultação e cancelamento; ainda é necessária confirmação no jogo.
