# Etapa 2 — contratos nativos e adaptador de leitura

## Comprovado no SRC 2.4.1 disponível

| Contrato | Fonte |
| --- | --- |
| Limites do mapa em dois Vector2 | `gui/Scaleform/daapi/view/battle/shared/minimap/component.py`, `getBoundingBox()` |
| Textura escolhida pela arena | Mesmo ficheiro, `_getMinimapTexture()` -> `arenaVisitor.type.getMinimapTexture()` |
| Entradas do plugin de veículos | `common.py`, `EntriesPlugin._entries`; o dicionário é interno, sensível à versão |
| Estado de publicação | `entries.py`, VehicleEntry: `isActive/isAlive/isInAoI/getLocation/getClassTag/getMatrix/isEnemy` |
| Posição da entrada nativa | `gui/battle_control/minimap_utils.py`, `Math.Matrix(matrix).translation` |
| Matriz só de translação | `gui/battle_control/matrix_factory.py`, `makeVehicleEntityMP` usa WGTranslationOnlyMP; não há yaw disponível nesta matriz |
| Pelotão e nome apresentado | `gui/battle_control/arena_info/arena_dp.py`, `isSquadMan(vID=...)`; `battle/minimap_enhancements.py` já usa `getVehicleInfo/getDisplayedName` |
| Coordenadas de clique clássico | `classic/minimap.py`, ClassicMinimapPingPlugin._getClickPosition -> makePointMatrixByLocal |
| Área lógica de input | `gui/battle_control/minimap_utils.py`: MINIMAP_SIZE=(210.0,210.0), independente do tamanho visual |
| Normalização de mapa | getPositionByLocal e makePointInBBoxMatrix: x cresce para a direita, z cresce para cima; aplica-se o centro real do bounding box |

## O que foi implementado

`views/battle/tactical_minimap.py` contém uma factory explícita e um adaptador de leitura. Não está registado em `getBattleViews`, no catálogo de interfaces, nem instalado por hooks. A factory lê as constantes do cliente, rejeita XVM e classes de plugins não auditadas antes de criar o adaptador. Uma substituição posterior do plugin invalida o snapshot. A filtragem de classe não deteta todo o tipo de monkeypatch de terceiros; isso continua pendente.

O adaptador só amostra matrizes depois de confirmar que a entrada está ativa, viva, em AoI e com localização AOI. UNDEFINED, FAR e AOI_TO_FAR são omitidos nesta primeira etapa conservadora, assim como destruídos. Não completa dados por entidades, não memoriza posições e não deduz orientação. A ausência de FAR implica que este ainda não é um minimapa completo.

O snapshot identifica-se como `native-minimap-audit`, é explicitamente parcial e lista as funções ausentes. O renderer sintético recusa essa origem: o adaptador não foi ligado à interface. O campo `nativePresentationChanged=false` descreve que não altera a apresentação; não pretende medir se o jogador ocultou o minimapa.

Não guarda proprietários nativos vivos: referências fracas, close idempotente e estado indisponível depois de destruição. Uma entrada inválida é omitida sem quebrar as restantes. Não cria listeners, polling, callbacks, comandos ou ficheiros.

`core/tactical_minimap.py` ganhou `world_point()` e `native_click_point()`. A segunda converte um ponto normalizado em coordenadas locais nativas; **não envia pings**. O chamador tem de fornecer MINIMAP_SIZE real. Isto confirma a matemática para o minimapa clássico, não paridade de input em epic/PvE nem captura de foco/modificadores/zoom.

## Testes e fronteira da fase

Testes em Python 2.7 e 3 cobrem amostragem das entradas publicadas, exclusão antes de ler matrizes, falha por entrada, ausência de retenção, destruição do proprietário e close. Os testes de geometria cobrem centro/cantos de retângulos deslocados e os 210 px lógicos. O teste Node confirma que o renderer continua a rejeitar snapshots nativos.

Não foi efetuado um teste em batalha. A próxima etapa continua a ser uma ponte diagnóstica explícita ao ciclo de vida e ao HUD, com handshake, sem ocultar o nativo; antes disso é necessário definir transporte de recursos e critérios de capacidade. Settings/seleção Driftkings continuam indisponíveis. O gate de produção e Lost Contact mantêm-se bloqueados.

Validação local desta etapa: 46 testes Core em cada versão Python (2.7/3), incluindo os novos contratos; factory também testada com stubs das importações reais. BattleSessionProvider declara `__weakref__` no SRC. Não foram introduzidos comandos de rede ou hooks.
