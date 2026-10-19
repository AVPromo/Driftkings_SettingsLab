# Compatibilidade WoT 2.4.1 — estado da entrega

| Área | Estado | Evidência / teste pendente |
| --- | --- | --- |
| Cliente EU 2.4.1.0 #977 | Auditado | version.xml, SRC e recursos SWF gui-part*.pkg |
| Minimap nativo | Preservado | Nenhum hook ou ocultação introduzido nesta entrega |
| Default Vanilla | Testado como política | DEFAULTS e selection(); JSON de produção não alterados |
| Escolha persistida em Settings/perfis | Pendente | Nenhum controlo de produção foi exposto |
| Falha Gameface / recurso indisponível | Política bloqueada testada | Sempre Vanilla; falta handoff e falha reais |
| Matemática de coordenadas | Testada | Centro, cantos, retângulo deslocado, limites e inválidos |
| Orientação | Convenção do protótipo testada | Norte=+z ainda precisa comparação no minimapa real |
| SVG/CSS no Gameface | Não validado | Sem assumir APIs de browser disponíveis no jogo |
| Render incremental e dispose | Testados em Node com DOM falso | Não medem compositor Gameface ou memória real |
| Lost Contact / inimigos invisíveis | Bloqueados | Sem ativação; rejeição antes de ler coordenadas; sem cache |
| Cartografia real, círculos e pings | Pendentes | Métodos/fontes nativos identificados; não ligados ao protótipo |
| Zoom/cliques/teclado nativos | Mantidos no sistema atual | Novo renderer não é carregado; equivalência futura não testada |
| XVM e outros mods | Não suporta substituição | Conflito é motivo de bloqueio; não foi testado com XVM instalado |
| Regular/epic/PvE/espectador/replays | Pendente em cada contexto | Não declarar suporte porque RandomHUDView existe |
| Ciclo batalha/desconexão/reentrada | Não integrado | Dispose do protótipo testado, eventos reais por ligar |
| Performance / FPS / DPI | Não medidos | Nenhuma promessa numérica |

As mesmas limitações aplicam-se a NA/ASIA; não se deduz compatibilidade de minimapa apenas porque a versão é igual. Os recursos Gameface de hangar já comparados noutra tarefa não provam compatibilidade deste minimapa.

## Critério para avançar

Uma fase em produção só pode ser marcada concluída com prova do contrato real e testes no jogo. O critério final do pedido — escolher o novo renderer sem perda de funções — **ainda não está satisfeito**. Esta entrega satisfaz a alternativa autorizada de protótipo isolado e infraestrutura segura, identificando as lacunas para continuar.

## Verificação local desta fase

- Core: 36 testes em Python 3 e 36 em Python 2.7, incluindo seis testes novos do minimapa.
- Settings: 25 testes em cada versão Python; testes JS existentes e novo renderer passam.
- Lint ES5 e sintaxe dos JS próprios verificados; defaults gerados e 18 catálogos i18n continuam sincronizados.
- Build debug completa: 266 módulos Python, sem ativação do protótipo.
- Dois testes do instalador falham por copiarem as imagens locais para fixtures que assumem ausência de branding/previews. O ficheiro destes testes e o código do instalador não foram alterados nesta fase; a falha é independente do minimapa. Não se declara CI global verde a partir deste resultado.
- Sem inspeção visual automática, combate real ou medições de desempenho nesta sessão.

## Etapa 2

A convenção x/direita, z/norte e a área lógica de clique de 210×210 foram confirmadas no SRC do minimapa clássico. Existe agora um adaptador de leitura parcial não instalado e sem ligação ao renderer; ver CONTRATOS_NATIVOS.md. O transporte de rotação não é fornecido pelas matrizes de veículos auditadas. A validação em combate, modos diferentes, input completo e fallback de ponta a ponta continua pendente.

## Etapa 3

Foi implementada a ponte diagnóstica para RandomHUDView, desligada por defeito. O recurso R e os assets são empacotados e a factory, os handlers e o protocolo foram testados com stubs/DOM falso. Não há ainda confirmação de carregamento no cliente, em batalha ou replay. A seleção de renderer continua bloqueada. Ver TESTE_GAMEFACE.md para o procedimento de teste e resultados esperados.

## Etapa 4

SVG DOM será sondado por uma grelha diagnóstica opt-in. API ausente ou que falhe na criação é tratada localmente; o reporte não altera o modo efetivo Vanilla. A construção de nós e a escala lógica são testadas em Node, mas SVG, cores, rasterização e DPI precisam de confirmação visual no Gameface. Ver TESTE_GRAFICO.md.
