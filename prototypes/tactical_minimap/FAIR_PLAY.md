# Tactical Minimap — avaliação Fair Play

Fontes oficiais consultadas em 19-10-2026:

- [EU: Prohibited Mods](https://worldoftanks.eu/en/content/guide/fair-play/prohibited-mods/).
- [WG Support: política de jogo limpo](https://www.wargaming.net/support/es/products/wot/article/10241/).

As regras vedam revelar posições por vias não disponibilizadas pelo cliente, incluindo inferências por objetos destruídos/tracers e certas apresentações de inimigos fora de visão. Não interpretar a capacidade técnica de ler dados como autorização de publicação.

O código nativo contém `convertToLastSpottedVehicleMP` e condições de visibilidade em `ArenaVehiclesPlugin._hideVehicle`. É evidência de um comportamento oficial condicionado, não autorização para criar um rastreador próprio ou ignorar essas condições. Falta confirmar formalmente o âmbito permitido para a apresentação proposta, além da integração técnica.

## Limites desta entrega

- Não há ligação automática de dados de batalha ao renderer nem enumeração de entidades. A etapa 2 contém um leitor nativo não instalado, limitado a entradas vivas publicadas em AoI.
- O renderer só aceita fixtures com origem `synthetic-preview`. O leitor nativo parcial produz `native-minimap-audit`, origem recusada pelo renderer.
- Entradas invisíveis/lost são descartadas antes de ler posição; snapshots são independentes e não guardam posições passadas.
- Lost Contact não tem opção de ativação, feed nem renderização. Existe apenas um SVG de referência, não utilizado pelo preview.
- Não há predição, projéteis, rastos, objetos destruídos, ghost markers 3D ou inferência.
- Uma futura integração terá de reproduzir exclusivamente o que o cliente publica e remover de imediato o que deixa de estar autorizado. Verificação específica por região e versão antes de disponibilizar.

O bloqueio descrito aplica-se apenas ao Tactical Minimap V2. Não é uma revisão de conformidade nem uma alteração silenciosa dos recursos legados do minimapa já existentes.
