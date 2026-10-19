# Cartografia e calibração — diagnóstico

A textura original vem de `ArenaVisitor.type.getMinimapTexture()`. Não é copiada para o pacote. O Gameface nativo do treino de mapas utiliza `img://spaces/.../mmap.dds` em fundos CSS; o diagnóstico usa o mesmo mecanismo, com caminhos virtuais restritos.

A amostra é uma imagem estática sem veículos, pings ou interação. O minimapa nativo continua ativo. A geometria vem de `currentTopLeftPoint` e `getMinimapRectBySizeIndex`, convertida para o palco Flash. Não encaminha cliques.

## Verificação no jogo

1. Compilar e instalar manualmente o pacote debug. Ativar `tacticalDiagnostics` no perfil utilizado e reiniciar o cliente.
2. Abrir batalha/replay: confirmar a amostra da cartografia junto do diagnóstico, sem fundo vazio ou distorção.
3. Alterar o tamanho do minimapa e a resolução: confirmar que os números de área/palco acompanham a mudança.
4. Testar ecrã inteiro, janela, ocultação da interface e saída de batalha. O diagnóstico deve desaparecer sem afetar o minimapa original.
5. Desativar a opção e reiniciar para retirar o diagnóstico.

A compilação e os testes automáticos não confirmam a pintura da textura nem a correspondência visual da área. Estas verificações continuam pendentes. Ainda não existe substituição do minimapa nem Lost Contact.

## Correspondência Flash / Gameface

Cartografia e geometria da etapa anterior confirmadas pelo utilizador no jogo.

O diagnóstico acrescenta agora apenas um contorno tracejado magenta e cinco pontos fixos: NO, NE, SO, SE e centro (+). As coordenadas do palco Flash são normalizadas e aplicadas em percentagens ao viewport Gameface. Não há textura adicional sobre o minimapa nem leitura de posições de veículos.

Confirmar que os quatro cantos coincidem com a área do mapa e o + com o centro, em vários tamanhos de minimapa, janela/ecrã inteiro e resoluções. Confirmar também ocultação do HUD e saída de batalha. Qualquer desvio é evidência de diferenças entre os viewports, não deve ser compensado com constantes antes de medir a causa. O contorno não interceta rato/teclado. Esta correspondência visual continua pendente de teste.

## Ponto aliado de calibração

O utilizador confirmou o alinhamento dos cinco pontos, incluindo a mudança de tamanho.

A etapa seguinte mostra um único `A` verde na posição de um aliado/pelotão atualmente publicado pelo minimapa nativo. Reutiliza o timer Flash existente de 250 ms, apenas no diagnóstico opt-in. Exige handshake e geometria válidos. Não transporta IDs, nomes, inimigos, posições antigas ou orientação. Reavalia as entradas em cada amostra; remove o ponto quando nenhuma é elegível. O aliado escolhido pode mudar se mudar a ordem das entradas nativas.

Confirmar se A coincide com um aliado nativo, também com veículos em movimento, redimensionamento e mapas diferentes. Confirmar ocultação do HUD e fim de batalha. O ponto é uma amostra de calibração, não um renderer de veículos nem garantia de sincronização por frame. O minimapa nativo continua responsável por todas as funcionalidades. Teste visual desta etapa pendente.

## Correção da entrega de geometria

No teste NA, o log confirmou `waiting-geometry` apesar de existirem 14 entradas publicadas. A origem não estava a entregar geometria ao diagnóstico. Foi removida a dependência do callback Flash → Python: a view lê agora `as_minimapGeometry()` diretamente, através de `core.callbacks`, a cada 250 ms apenas com o diagnóstico ativo. O callback agendado é cancelado ao destruir a view e para em erro/desativação. O timer nativo do minimapa não foi alterado. Esta revisão substitui a descrição anterior de reutilização do timer Flash para o diagnóstico. Confirmar no próximo teste `Ponto A: ready` e a coincidência visual.

## Leitura independente da view auxiliar

O segundo teste continuou em `waiting-geometry`. Foi confirmado por hash que o SWF e os PYC instalados correspondiam à build. A ponte já recebe o componente nativo e as entradas, mas o caminho pela view auxiliar não produz geometria.

A biblioteca passa a expor `as_DriftkingsMinimapGeometry` no protótipo `BaseMinimap`, tal como já expõe as fábricas na página nativa. A ponte consulta o próprio `MinimapComponent.flashObject`, sem criar ou esperar por `MinimapCentredView`. Uma string limitada transporta seis números do palco, evitando conversão implícita de objetos GFx. A leitura repete-se a cada 250 ms pelo serviço existente de callbacks; é cancelada em ended/dispose, não lê quando o HUD está oculto e recupera caso a biblioteca ainda esteja a carregar. Foram removidos o getter e o polling da view auxiliar.

Esta revisão requer substituir o pacote e reabrir o replay. O teste visual permanece pendente; o log apresenta agora também `geometry=...`, distinguindo biblioteca indisponível, palco indisponível e dados inválidos.

## Ponto recebido mas oculto pelo Flash

O log NA de 19/10/2026 às 02:39:30 confirmou `status=ready`, 14 entradas e geometria válida. O mesmo log mostra `classicBattlePage` (Flash) na camada 4 e `randomBattleHud` (Gameface) na camada 3. Isto explica a provável ocultação do ponto pelo fundo do minimapa original; um z-index CSS não atravessa janelas nativas.

O A passa agora a ser desenhado exclusivamente na pequena amostra da cartografia junto ao painel diagnóstico. A legenda indica claramente «Mapa de teste — A = aliado» e o texto mostra as percentagens horizontal/vertical. A textura é reutilizada; só o ponto muda. Não são alteradas as camadas nem a visibilidade do original. Confirmar o A nesta amostra, não no minimapa original. A possibilidade de substituição futura continua bloqueada por paridade e gestão de camadas. A indicação anterior para procurar o A sobre o original estava incorreta.

## Grelha nativa e confirmação de coordenadas

O utilizador confirmou que o A aparece na amostra. Acrescentada grelha 10 × 10: colunas `1234567890` da esquerda para a direita e linhas `ABCDEFGHJK` de cima para baixo. A amostra passou para 200 rem para permitir ler os rótulos. A textura e grelha são conservadas entre atualizações; apenas o ponto é renovado.

O adapter obtém a célula do mesmo x/z e bounding box usados para normalizar a posição, chamando as funções do cliente `getCellIdFromPosition(..., 10)` e `getCellName(..., 10)`. O texto mostra «Célula nativa: ...». Isto evita uma segunda implementação de arredondamento: nas linhas exatas da grelha, o cálculo nativo inverte o eixo z antes de determinar a linha e aplica uma margem de 0,1 m nos limites. Não é correto inferir sempre a célula com floor(y * 10).

Para validar: confirmar a célula escrita contra a célula onde o A verde aparece na amostra, e comparar esse local com o aliado no mapa original. Testar perto dos quatro cantos, atravessando linhas e com outro mapa. Norte = +z, direita = +x, origem normalizada = canto superior esquerdo. A divisão considera a bounding box real, incluindo mapas deslocados ou retangulares. Não são enviados x/z mundiais, IDs ou nomes. Confirmação visual da grelha pendente.

## Ícone de classe do aliado

O utilizador confirmou a correspondência do A com a grelha/célula. A amostra substitui agora esse ponto pelo ícone da classe nativa: ligeiro, médio, pesado, caça-tanques ou artilharia. Continua a mostrar apenas um aliado elegível. Verde = aliado; amarelo = pelotão. A classe e a célula permanecem escritas no diagnóstico. Sem classe reconhecida ou SVG disponível, conserva o A como alternativa. O nó SVG é reutilizado quando só muda a posição; elimina-se quando não existe aliado elegível.

Confirmar que a silhueta corresponde ao tipo do aliado e que mantém a célula correta em movimento. Validar cor do pelotão quando disponível. A amostra não lê inimigos, não conserva posições antigas e não substitui o minimapa nativo. Teste visual desta etapa pendente.

## Vários aliados na amostra

Classe/cor/posição do marcador individual confirmadas pelo utilizador. A etapa atual mostra todos os aliados elegíveis do snapshot nativo, limitados a 64 entradas processadas por amostra. Mantém os filtros anteriores: vivos, ativos e em AoI; não inclui aliados distantes, inimigos, mortos ou Lost Contact. O contador distingue a amostra parcial da equipa completa.

Não transporta IDs/nome/histórico. Usa slots do snapshot atual para reutilizar os nós de classe/cor, atualiza posições a cada 250 ms e remove slots ausentes. Uma lista vazia elimina todos os ícones, mesmo se existir a referência individual antiga no payload. A célula/classe escrita continua a referir-se ao primeiro aliado, não a cada ícone.

Confirmar vários ícones na pequena amostra, posições em movimento e cores de equipa/pelotão. Confirmar remoção quando o aliado morre ou deixa AoI, ocultação do HUD e fim de replay. O minimapa original permanece ativo; a paridade do minimapa alternativo ainda não está concluída.

## Ícone do próprio veículo

O adapter compara o ID da entrada publicada com `arenaDP.getPlayerVehicleID()` e marca `side=player`. O transportador preserva esta relação sem enviar o ID. O renderer usa o chevron branco `player` em vez da classe; mantém verde para aliados e amarelo para pelotão. Sem suporte SVG, usa TU.

A orientação ainda não está ligada: a matriz das entradas de veículos foi verificada apenas para translação. A seta é atualmente um identificador fixo, não um indicador de direção. Não se infere rotação a partir de deslocamento. Só se desenha o próprio veículo quando existe uma entrada elegível no plugin de veículos; a entrada pessoal/câmara, usada pelo cliente em outros modos, continua por integrar. Confirmar o chevron no replay testado. A classificação usa o veículo do jogador, não transforma o veículo observado em jogador após morte.

## Entrada pessoal nativa do jogador

A mudança de relação na lista de veículos não bastou: o cliente utiliza `ViewPointMinimapEntry` para a seta própria. A ponte passa a ler o glifo pessoal já publicado no Flash, com posição relativa à área do mapa e direção obtida pela transformação do próprio desenho. Não consulta entidades nem deduz direção pelo movimento.

A leitura só é solicitada se o plugin pessoal tiver o mesmo ID próprio e controlado, e a informação nativa indicar jogador vivo e não observador. No Flash, exige entrada/seta visível e alpha positivo; a procura na árvore é limitada a 4000 nós. Um protocolo de string opcional e validado transporta x/y/ângulo. A entrada pessoal substitui qualquer duplicado do jogador na lista de veículos e não conserva posição se desaparecer. O texto «Seta própria: publicada» e `player=True` no log distinguem a disponibilidade. A seta branca deve aparecer na amostra e rodar como a seta original; falta confirmação no jogo.

## Correção de posição própria e aliados fora de AoI

A captura do utilizador mostrou o deslocamento/intermitência da seta e aliados ausentes. A posição própria deixa de ser obtida através da árvore visual/zoom do Flash. O diagnóstico observa apenas a publicação nativa de `ViewPointEntry`/`personal` em addEntry/setMatrix/setActive/delEntry. Conserva a referência à matriz publicada, ID técnico da entrada e estado ativo, nunca coordenadas antigas. Em cada amostra, lê a posição mundial atual e yaw dessa matriz e usa a mesma transformação world/bounds dos aliados. Verifica ainda ID pessoal/controlado, vivo e não observador. Eliminação, desativação, fim de batalha e dispose libertam a entrada. Os quatro hooks são exclusivos do diagnóstico opt-in e preservam as chamadas originais.

Aliados vivos e ativos em FAR passam a ser aceites quando o próprio minimapa os publica. Inimigos FAR/transicionais continuam excluídos antes de ler qualquer matriz. Os mortos continuam fora da amostra atual. Não há pesquisa de entidades nem reconstrução de posições.

Confirmar seta/célula em movimento com e sem zoom original e depois fora de AoI dos aliados. O ajuste visual anterior foi removido, sem constantes de compensação. Testes cobrem FAR aliado versus inimigo, posição própria em bounds deslocados, yaw, correspondência de ID, substituição/desativação/eliminação da matriz publicada. Falta confirmação no jogo.

## Bases e pontos de controlo clássicos

O utilizador confirmou a correção da posição própria e dos aliados distantes. Acrescentadas posições de bases aliadas/inimigas e pontos de controlo publicados por `TeamsOrControlsPointsPlugin` do cliente clássico. Fonte auditada: classic/minimap.py (`__addBaseEntry`, `__addTeamBasePositions`, `__addControlPoints`) e shared/minimap/settings.py. Apenas `AllyTeamBaseEntry`, `EnemyTeamBaseEntry` e `ControlPointEntry` no contentor `points` são aceites.

Reutiliza os quatro hooks de publicação existentes: criação, matriz, ativação e eliminação. Sem novo timer. Conserva apenas a matriz nativa e o estado atual, limitados a 16 entradas; elimina dados no fim da batalha/dispose. Aplica os mesmos bounds mundiais da amostra. O contrato transmite apenas tipo/x/y, sem IDs ou texto arbitrário. Uma falha nos objetivos não desativa os aliados.

Bandeira verde = base aliada; vermelha = base inimiga; símbolo branco = ponto de controlo. Sem SVG, usa B/C. Os nós são reutilizados e removidos quando a entrada desaparece. Não inclui números, estado/progresso de captura, cliques ou pings. Objetivos especiais de Frontline/outros modos continuam por auditar. Não confundir base inimiga pública com posição de veículo inimigo.

Confirmar no replay as duas bases e respetivas células; testar encontro/controlo quando disponível, zoom original e saída de batalha. O contador «Bases/objetivos» ajuda a distinguir falta de publicação de falha de desenho. Confirmação visual pendente.

## Identificação e captura clássica

Posições das bases confirmadas pelo utilizador. A amostra lê agora o número enviado pelo cliente através de `invoke(entryID, setPointNumber, number)`; acrescentado um único hook ao conjunto existente, sem timer novo. Número 0 corresponde a ponto sem numeração e não é desenhado. Não renumera bases por ordem da nossa lista.

A captura vem de `session.shared.teamBases`, restringindo o contrato ao módulo nativo clássico `team_bases_ctrl`. Usa `makeClientTeamBaseID`, `isTeamBaseCaptured` e o accessor nativo `_getPoints` (points/timeLeft/invaders/stopped). Bases são associadas à equipa, número e posição publicados pela arena; pontos neutros consultam as equipas disponíveis definidas pelo próprio controlador. Não usa o estado `attack/reply` do minimapa como captura e não extrapola tempos/progresso.

A amostra mostra percentagem/barra durante captura, PAUSA quando bloqueada, OK após captura e ? se o contrato não estiver confirmado. Os valores são limitados e validados; estados ausentes nunca são tratados como captura livre. Reset nativo volta a idle e oculta a barra. Ainda não suporta captura de objetivos especiais de Frontline/outros modos nem ações de clique.

Teste: comparar número, percentagem e bloqueio com o painel de captura do jogo num replay com captura. Confirmar reset após saída dos invasores e conclusão a 100%. Não é necessário fazer uma batalha real para tentar este teste, mas o replay precisa de conter estes eventos. Testes automáticos cobrem leitura atual, captura/bloqueio/conclusão/reset, controlo neutro e limites do contrato; confirmação visual pendente.

## Novos SVG fornecidos pelo utilizador

Identificação/captura testadas e confirmadas pelo utilizador. A biblioteca passa a usar os desenhos completos de `prototypes/tactical_minimap/icons`: grupos, retângulos, caminhos, círculos, transformações e gradientes, com viewBox 64 × 64. Os tons claros são adaptados à cor da relação (verde/amarelo/branco); detalhes escuros e acentos de estado mantêm a cor original. Cada instância recebe IDs de gradiente únicos. Bases e pontos de controlo conservam os símbolos anteriores.

As definições são geradas no bloco identificado de `TacticalMinimap/graphics.js`, sem parser XML em runtime nem nova dependência de carregamento. Após editar os SVG: `python build_tools/generate_tactical_icons.py --write`; para verificar: `python build_tools/generate_tactical_icons.py --check`. O teste Node compara hashes dos ficheiros de referência e geometria completa dos paths, retângulos, transformações, cores e referências de gradiente. O renderer conserva o nó SVG quando só muda a posição.

O desenho de destruído foi atualizado para o preview; a amostra de batalha continua a mostrar veículos vivos. Lost Contact foi guardado apenas como referência e continua excluído da biblioteca/runtime. Confirmar no Gameface real a pintura dos gradientes, legibilidade a 18 px e rotação da nova seta. A construção DOM por si só não comprova a pintura.

## Círculos de alcance publicados pelo cliente

Acrescentada a entrada nativa `ViewRangeCirclesEntry`/`personal`, acompanhada pelos hooks já existentes de criação, matriz, ativação, invoke e eliminação. Não foram acrescentados hooks nem timers. As chamadas as_addDrawRange/as_addDynamicViewRange/as_addMaxViewRage/as_addMinSpottingRange fornecem raio, cor e alpha; as_updateDynRange atualiza visão dinâmica; as_del*/as_removeAllCircles removem os desenhos.

O centro vem da matriz mundial publicada para a entrada. Raio horizontal = metros/largura dos bounds; vertical = metros/altura. A amostra desenha elipses em percentagens e recorta o exterior ao mapa, mantendo veículos/objetivos por cima. Respeita o estado ativo e as remoções do cliente, sem completar raios por defaults ou previsões. O payload limita-se aos quatro tipos conhecidos e valida cores/raios/opacidade.

Testar no replay comparando centro, tamanho e cores com os círculos originais. Alterar as opções nativas de círculos, testar visão dinâmica e confirmar que desaparecem quando o original é desativado/oculto. O contador «Círculos nativos» indica quantos foram publicados. Não inclui círculos adicionais personalizados, setores de câmara/canhão ou ações de rato. Testes Python/Node cobrem comandos, ciclo de vida, limites, movimento e proporções retangulares; pintura no Gameface pendente. A validação visual dos novos gradientes SVG também continua pendente.

## Receção de pings nativos

### Zona de mira da artilharia

Células a piscar confirmadas no jogo. Acrescentado `ArtyMarkerMinimapEntry`, mapeado pelo cliente de `SPG_AIM_AREA_SUBTYPE` em `AreaStaticMarkerPlugin`. Usa o contentor `equipments` e a matriz publicada, com os mesmos hooks existentes e remoção nativa. A amostra desenha uma mira laranja (+); não calcula dispersão, raio, previsão de impacto ou posições de artilharia inimiga. Confirmar posição e desaparecimento contra o marcador original num replay que contenha esse evento. Não inclui os efeitos de consumíveis de artilharia nem indicadores de disparos inimigos.

### Correção das células a piscar

O utilizador confirmou que as células piscavam no original mas faltavam na amostra. Essas animações usam `SimpleAttentionToFlashMinimapEntry`, separadamente dos marcadores estáticos descritos abaixo. A ponte Flash lê apenas animações atualmente visíveis e ainda em curso, limitada a 4000 nós e 32 células. Converte o centro dos limites visuais para o centro de uma célula da grelha 10×10; outras dimensões não são aceites.

A amostra mostra um quadrado amarelo com a largura e altura de uma célula. Reutiliza a amostragem existente, sem criar TTL, histórico ou comandos. Quando a animação desaparece ou termina, o destaque é removido no próximo frame amostrado. O log `Ping diagnostics: static=… visibleCellAnimations=…` ajuda a confirmar a leitura. Compilação e testes automatizados não substituem a confirmação visual: comparar posição, início e remoção num replay com células a piscar no original.

Círculos confirmados pelo utilizador. A etapa seguinte espelha as entradas `MarkAttentionEntryUI` e `MarkGoingToPositionEntryUI` no contentor `equipments`, publicadas por AreaStaticMarkerPlugin a partir das comunicações do cliente. As fontes auditadas são shared/minimap/plugins.py (`_LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME`, `__addStaticMarker`, `__delStaticMarker`) e settings.py. O segundo símbolo também é usado pelo waypoint nativo de pré-batalha; não se inventa uma distinção que o símbolo não fornece.

Reutiliza os oito hooks e o callback de amostragem existentes. Estado attack/idle/reply vem de setState. A duração pertence ao cliente: a amostra remove quando há setActive(false)/delEntry e não cria TTL, relógio ou animação própria. Limite de 32 entradas; payload apenas tipo/x/y/estado, sem remetente, texto ou ID. Exclui símbolos não auditados, incluindo UnspottedMarkerUI. O fim de batalha/dispose liberta todas as referências de matriz.

Na amostra: ! amarelo = atenção; > azul = destino/waypoint; R = resposta; idle usa menor opacidade. Confirmar posição e remoção contra o original num replay com comunicações gravadas. O plugin de envio por clique é desativado pelo cliente em replays; isto não impede que marcadores recebidos/gravados sejam publicados. Um replay sem esses eventos pode manter o contador a zero. Não há envio de comandos, resposta automática ou interceção de cliques. Pings sobre veículos/bases, áreas de artilharia e outros estados de comunicação continuam fora deste contrato parcial.
