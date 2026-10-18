# Tactical Minimap V2 — auditoria da Fase 0

Data: 19-10-2026. Âmbito: repositório local, SRC EU disponível e cliente EU 2.4.1.0 #977. Não foi aberto um combate para esta auditoria. As eliminações manuais de documentação do instalador não fazem parte deste trabalho.

## Estrutura e integração existente

Foram inventariados os diretórios: cliente Driftkings (267 ficheiros), Gameface (66), Flash source (50), build_tools (25), build_data (8) e tests (10), antes das alterações desta fase. `build_data/components.json` é o manifesto; `component_list.py` e `interface_catalog.py` são gerados/validados pelo catálogo. `settings/definitions/`, service/store/loader, perfis, `core/battle_events.py` e `core/battle_policy.py` constituem os pontos existentes de integração. Não foi criado outro carregador de mods.

## Factos comprovados no código

| Área | Evidência e conclusão |
| --- | --- |
| Minimap nativo | SRC `client/gui/Scaleform/daapi/view/battle/shared/minimap/component.py`: `MinimapComponent` herda `MinimapMeta`; `_createFlashComponent()` instancia `GUI.WGMinimapFlashAS3`; `_populate/_dispose` iniciam/param plugins e removem entradas. É Scaleform/Flash, não Gameface. |
| Cliente EU instalado | Em `res/packages/gui-part4.pkg` existe `gui/flash/minimap.swf`; em gui-part1 existem as bibliotecas de entradas e PveMinimap; em gui-part3 epicMinimap. Não foram encontrados recursos Gameface de minimapa nos quatro gui-part*.pkg pesquisados. Isto não prova ausência de todos os recursos em todos os modos. |
| Driftkings atual | `battle/minimap_enhancements.py` estende `PersonalEntriesPlugin` e `ArenaVehiclesPlugin`; `views/battle/minimap_enhancements.py` e `meta/battle/minimap.py` publicam opções em AS3; `flash_source/battle/src/driftkings/battle/components/minimap/MinimapCentred.as` manipula o `BaseMinimap` existente. |
| Settings | `settings/definitions/battle/minimap_enhancements.py`, `core/minimap.py` e `settings/minimap_store.py`; quatro documentos `minimap*.json` e validação/perfis existentes. O modo alternativo atual é apresentação/zoom Flash, não um renderer Gameface. |
| Recursos | Sete PNG `MinimapAim_0..6.png`, símbolos e bibliotecas SWF nativos, cartografia de `arenaVisitor.type.getMinimapTexture()`, limites de `getBoundingBox()`. Não inventar caminhos de mapas. |
| Dados nativos | Component aceita matrizes, ativação e chamadas por entrada. Plugins usam `matrix_factory`, posições fornecidas pela arena, círculos e feedback. Matrizes dinâmicas são consumidas também pelo componente C++; eventos Python de avistamento não representam um stream completo de posições/rotação em cada frame. |
| Input | `onMinimapClicked(x,y,buttonIdx,mapScaleIndex)` delega nos plugins; `applyNewSize()` também. Os controlos Flash e o componente C++ participam no zoom, coordenadas e interação. Encaminhar apenas o clique não garante equivalência. |
| Gameface | `ui/gameface.py` usa Wulf, recursos R registados e `openwg_gameface.gf_mod_inject`; dependência declarada `net.openwg.gameface_1.2.2.wotmod`. `views/battle/battle_marks_of_excellence.py` já liga um ViewComponent ao `RandomHUDView._getChildComponents`. Isto confirma painéis Gameface em batalha, não a substituição de WGMinimapFlashAS3. |
| Ciclo de vida | `core/battle_events.py`: sinais compartilhados loaded/started/ended/visibility e aquisição/libertação por proprietário; os views Gameface existentes têm finalize/dispose. Reutilizar estes limites numa integração futura. |
| Terceiros | O hook `_setupPlugins` atual consulta `xvmInstalled` e evita instalar os plugins Driftkings com XVM. Preserva subclasses específicas dos modos. Não existe prova de interoperabilidade com todos os outros mods de minimapa. |
| Linguagens | Cliente Python 2.7; ferramentas Python 3. JS próprio usa ES5 e ESLint ecmaVersion 5. Os bundles nativos podem conter outra sintaxe; não copiar essa sintaxe para o novo renderer. |

## Lost Contact e Fair Play

O SRC `plugins.py`, `ArenaVehiclesPlugin._hideVehicle`, chama `matrix_factory.convertToLastSpottedVehicleMP`, muda a localização para UNDEFINED e usa flags do cliente para desativar ou mostrar a última posição. Há, portanto, suporte nativo condicionado. Isso não autoriza automaticamente capturar/coletar/reter posições num renderer próprio.

A política oficial proíbe revelar posições por meios não previstos no cliente e outras vantagens indevidas: [EU Prohibited Mods](https://worldoftanks.eu/en/content/guide/fair-play/prohibited-mods/) e [suporte WG](https://www.wargaming.net/support/es/products/wot/article/10241/). A leitura feita não fornece uma autorização explícita para a reprodução proposta. Não se conclui que todo o ícone de última posição seja proibido; conclui-se que falta validar o contrato e a autorização deste novo componente.

Decisão: Lost Contact bloqueado em produção. Só existe recurso gráfico de referência no protótipo, sem alimentação de coordenadas inimigas e sem controlo para ativação. Não usar BigWorld.entities, retenção de coordenadas, inferência, tracers ou predição.

## Lacuna crítica e decisão

Existe uma via comprovada para desenhar um painel Gameface em batalha, mas não um contrato completo validado que replique o input e todas as entradas do minimapa Flash, mantenha os dois sistemas sincronizados e faça fallback atómico em falhas JS/Python. Ocultar o nativo hoje arriscaria perder zoom, pings e cliques ou deixar a batalha sem minimapa.

Seguindo a alternativa expressamente prevista no pedido, esta entrega avança apenas com protótipo isolado e infraestrutura pura de validação/transformação/fallback. O protótipo não é carregado no jogo, não modifica defaults, não declara recursos R nem cria hooks. O modo Driftkings permanece bloqueado na política de produção, mesmo com uma preferência guardada. Não é apresentado como minimapa funcional em batalha.

## Hipóteses e validação pendente

- Transporte de matrizes/rotação e equivalência de input para todas as entradas: investigar, não implementado.
- SVG, transparência, tipografia e transformações no Gameface efetivo: validar; o protótipo de navegador não é prova.
- Suporte regular/epic/PvE/espectador, replays e troca de veículo: validar separadamente; não declarar compatibilidade global.
- Categoria Settings Minimap, seleção Vanilla/Driftkings e política de aplicação: integrar apenas depois de resolver o gate de suporte e as traduções; não oferecer controlos fictícios.
- Troca de renderer: no máximo na entrada da batalha até existir uma transição comprovada. Nunca desligar o minimapa nativo antes do handshake e do contrato de input completos.
- Performance, resolução/DPI, fallback após perda do renderer, desconexão e conflitos: requerem testes dentro do jogo; não foram medidos FPS nem consumos.
