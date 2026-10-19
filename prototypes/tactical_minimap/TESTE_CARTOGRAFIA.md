# Cartografia e calibração — diagnóstico

## Clique concluído e cancelamento de arrastos

A correção de sniper foi confirmada pelo utilizador. Nesta etapa, o envio de uma posição passa de mousedown para um par pressão/libertação dentro da mesma imagem, botão, alvo e geração. Mover mais de quatro píxeis cancela o gesto, mesmo regressando ao ponto inicial. Mudança de geometria, perda de foco da janela, HUD/cursor desativado, remoção/recriação da vista ou erro de desenho invalidam o clique pendente. Pressionar sem libertar não envia comandos. O pedido continua deduplicado no Python e o handler nativo é chamado no máximo uma vez.

Auditoria reiterada de `Minimap.onMouseClickHandler`: o caminho de posição chama `onMinimapClickedS(x,y,buttonIdx,sizeIndex)`; a via `IHoverableEntity.onClick` é separada. Não foi encontrado um contrato específico de seleção dos ícones VehicleMinimapEntry; continuam em diagnóstico, sem conversão silenciosa para ping de posição.

Teste em Topography com cursor visível: clicar e libertar esquerdo/direito numa área livre; confirmar um único envio. Pressionar e arrastar não deve enviar ping. Pressionar, retirar Ctrl ou alternar janela e regressar não deve concluir um pedido antigo. Confirmar que passar o rato e clicar em ícones mantém a identificação em diagnóstico. O botão do meio e os replays continuam sem envio nativo.

Testes Node cobrem envio só na libertação, ausência de envio na pressão, arrasto com retorno ao ponto inicial, blur, mudança de geometria e bloqueio ao retirar a permissão de interação. Não há ainda ocultação do minimapa original.

## Recuperação da amostra após falha do Gameface

Uma exceção no desenho limpa os nós, alinhamento, hover e estado de interação. O payload que falhou deixa de estar marcado como desenhado, permitindo recuperação no próximo evento, mesmo com dados iguais. A troca do modelo remove a amostra anterior antes de ligar a nova; uma falha transitória ao subscrever o modelo também pode ser repetida sem manter os nós antigos ou duplicar callbacks.

Testes Node injetam falhas de desenho e subscrição e verificam remoção, recuperação e libertação final. O minimapa nativo continua sempre visível; esta etapa não implementa nem comprova recuperação de uma substituição real, ainda bloqueada. Confirmar no cliente a saída/entrada em Topography, reabrir uma missão e alternar visibilidade do HUD. Não foi introduzida uma falha artificial no jogo do utilizador.

## Preferências no painel e configurações

O painel de melhorias do minimapa contém agora a escolha Vanilla/Driftkings e as preferências `tactical`: tema, seguir o tamanho nativo ou tamanho fixo, opacidade da textura, escala dos ícones, grelha, nomes, tamanho de letra e cores de aliados/inimigos/pelotão. São guardadas pelo gestor existente em `minimap_enhancements/minimap.json`, incluindo perfis e reposição de valores. Os defaults antigos recebem os campos em falta pelo merge existente; não se substituem escolhas do jogador.

A escolha Driftkings é apenas uma preferência persistida. O modo efetivo permanece Vanilla; não oculta o original nem ativa automaticamente `tacticalDiagnostics`. Os controlos mostram este limite. As preferências visuais aplicam-se somente à amostra com diagnóstico ativo. As novas legendas têm fallback inglês; catálogos i18n não foram alterados nesta etapa.

Teste em Topography, após instalar o pacote e voltar a entrar na missão:
1. Nas melhorias do minimapa, guardar tema Military Green, grelha desligada, nomes desligados e cores distintas. Confirmar a apresentação na amostra e o minimapa original intacto.
2. Desativar seguir tamanho nativo e escolher um tamanho fixo. Confirmar que a amostra mantém esse tamanho ao alterar a escala nativa; cliques continuam baseados na geometria nativa, sem deslocamento.
3. Reativar seguir tamanho nativo e nomes/grelha; variar letra, escala dos ícones e opacidade. Apenas a textura deve escurecer; ícones continuam legíveis.
4. Guardar Driftkings, reabrir as configurações e confirmar a preferência. A mensagem deve indicar que Vanilla continua ativo. Verificar também guardar/carregar perfil e reposição por opção.

A temporização destas opções continua «próxima batalha», como as restantes opções do módulo. Confirmação visual no cliente pendente. Testes automatizados cobrem limites, valores inválidos, defaults independentes, payload separado da política de seleção e apresentação/restauro em DOM simulado.

## Identificação de ícones e separação do clique em posição

Redimensionamento confirmado pelo utilizador. A auditoria seguinte confirmou que `MinimapMeta.onMinimapClicked`/`MinimapComponent.onMinimapClicked` recebem x/y/botão/escala, sem ID de veículo. No Flash auditado, `VehicleMinimapEntry` expõe informação visual e highlight, mas não um onClick público; `Minimap.onMouseClickHandler` trata posições e entidades IHoverableEntity (implementação encontrada para W2GTBattleZoneMinimapEntry). Não foi encontrado um contrato verificável de seleção de veículo para reproduzir pelo Gameface nesta etapa. Não se inventou um comando de alvo.

A amostra reconhece o nó SVG/etiqueta do veículo a partir dos dados do frame corrente, sem enviar IDs ao JS. Com o cursor visível, passar o rato realça o ícone e mostra relação, classe, nome e estado de destruído abaixo da amostra. Marcadores de Topography continuam identificados como treino. Sem cursor, HUD ou handshake não há interação. Camadas de desenho deixam passar o rato até aos ícones/imagem; nenhum listener novo altera o cursor ou foco.

O comando distingue `target=position` de `target=vehicle`. O backend confirma cliques de veículo como `diagnostic-vehicle` e não os encaminha ao método de posições; há uma segunda proteção no helper nativo. Continua a encaminhar esquerdo/direito nos pontos livres. O alvo de diagnóstico não recebe comandos de ataque, seleção, mira ou chat. O listener de movimento é libertado em dispose/reload.

Testar em Topography: Ctrl esquerdo e passar o rato por objetivos, incluindo SVG e etiqueta; confirmar realce e texto. Clicar num ícone deve mostrar reconhecimento em diagnóstico, sem criar ping de posição. Clicar numa posição livre deve continuar a usar a via nativa. Confirmar limpeza ao retirar o cursor, remover um alvo e sair da missão. Validação in-game pendente. Seleção nativa específica de veículos permanece pendente e impede declarar paridade completa.

## Redimensionamento da amostra com o índice nativo

A amostra deixa de ter 200rem fixos: os índices nativos 0–5 correspondem a 200/240/280/320/360/400rem. É uma escala própria da amostra, não uma reprodução em pixels do tamanho original. Mantém a proporção do retângulo nativo quando válida e limita as dimensões à viewport, considerando a unidade rem. Sem geometria/índice válidos usa 200rem. Nenhuma preferência do jogo é alterada pelo código novo.

O evento resize da janela recalcula apenas dimensões CSS. Ícones, etiquetas, áreas e linhas continuam em posições normalizadas e os nós são reutilizados. O input usa getBoundingClientRect em cada clique e a constante lógica MINIMAP_SIZE no backend; não confunde o tamanho visual de 200–400rem com os 210 pixels lógicos nativos. O listener é removido no fim/reload da view.

Teste em Topography: usar as teclas nativas de aumentar/diminuir o minimapa e confirmar que a amostra também cresce/encolhe. Em dois tamanhos diferentes, clicar nos mesmos pontos relativos e comparar os resultados. Alternar resolução/tela inteira para verificar limite, proporções e legibilidade. A posição da amostra continua a ser a do painel de diagnóstico, não a do minimapa de produção. Validação no jogo pendente.

## Botão direito pela via nativa

Topography confirmado pelo utilizador. A amostra encaminha agora os botões esquerdo e direito; o botão do meio continua diagnóstico. Mantém o mesmo handler, validações de cursor/foco modal, modo, propriedade, coordenadas, geração e deduplicação. O clique direito usa `MinimapPingPlugin._specialMinimapCommand`: o próprio cliente tenta `AvatarInputHandler.onMinimapClicked` e só cria a marcação de destino quando esse controlador não o trata. O mod não decide quando mudar de câmara ou mover a mira.

Teste com Ctrl esquerdo e botão direito na amostra: em Topography/tanque normal, comparar a marcação de destino com o original; em artilharia, comparar a mudança/movimento de câmara conforme o comportamento nativo. Confirmar um único efeito por clique, também depois de redimensionar. Replays mantêm apenas diagnóstico, sem chamar o handler. Testes automatizados cobrem o índice nativo 1, bloqueios, deduplicação e ausência de encaminhamento do meio; falta validação visual/do comando no jogo. A amostra continua sem substituir o original.

## Topography / Maps Training

Ativação da amostra no modo pedida pelo utilizador. O cliente usa `MAPS_TRAINING_PAGE` com `RANDOM_BATTLE_HUD`, pelo que reutiliza a view Gameface existente. O adaptador aceita especificamente `MapsTrainingMinimapComponent` e `BotAppearNotificationPlugin` do módulo nativo maps_training, confirmando também `ARENA_GUI_TYPE.MAPS_TRAINING` na arena em cada snapshot. Uma troca de modo/plugin invalida o leitor; não se alargou a lista de plugins genéricos e os filtros das batalhas normais permanecem iguais.

O plugin de Topography publica entradas estáticas `MapsTrainingVehicleEntryUI` ativas para os alvos do exercício, mesmo com isInAoI=false e localização indefinida. São pistas visíveis do próprio modo, não inimigos avistados da batalha clássica. A amostra transporta-as num canal separado `trainingPoints`: laranja para marcador de treino, dourado quando `isGoalForPlayer()` assinala o objetivo atual. A etiqueta resolve o ID real com `getOwnVehicleID()`, pois o ID da entrada é o da marcação. Destruição e remoção seguem a entrada nativa, sem cache, pesquisa de entidades ou antecipação de objetivos futuros não publicados.

Textura, grelha, seta própria, círculos e input continuam nos contratos já existentes. O modo herda o plugin clássico de cliques; só se esse handler auditado estiver disponível se pode encaminhar um clique esquerdo. Não se alteram as regras/objetivos do exercício, e o minimapa original mantém as rotas, textos e elementos específicos que a amostra ainda não espelha.

Teste: instalar a build e iniciar uma missão de Topography. Confirmar a amostra, cartografia, seta própria e marcadores laranja/dourados contra os elementos visíveis no original. Concluir um objetivo e verificar atualização/remoção; sair da missão e abrir outra para verificar limpeza. Ainda necessita de confirmação no jogo. Continua a usar o opt-in tacticalDiagnostics existente; não ativa substituição do minimapa.

## Clique esquerdo encaminhado ao cliente

Receção Gameface confirmada pelo utilizador. A etapa atual acrescenta encaminhamento **só do clique esquerdo** para `MinimapComponent.onMinimapClicked`, depois de validar cursor, modal, geração, pedido e posição. A geometria/tamanho são relidos no momento da receção. A classe do plugin tem de ser exatamente `ClassicMinimapPingPlugin` do módulo clássico auditado; plugin ausente, terceiro/XVM, modo não clássico ou replay mantêm diagnóstico sem envio. Os outros botões continuam sem encaminhamento.

O código não chama diretamente APIs de chat nem procura alvos: o plugin original decide limites de envio, marcação de atenção/área de artilharia, resposta a marcador e base próxima. O resultado `forwarded` significa apenas que o método nativo foi chamado, não que um ping foi aceite pelo servidor. Não cobre ainda as interações específicas dos ícones de veículos.

Cada evento recebe um identificador crescente por geração. O backend grava esse identificador antes da chamada nativa; duplicações, repetição reentrante e gerações antigas são rejeitadas. Falhas nativas não são repetidas. Não há fila, callback de reenvio ou timer novo. Um clique intencional posterior recebe outro identificador e segue as regras normais do cliente.

Teste numa batalha real: mostrar cursor com Ctrl esquerdo e clicar uma vez numa posição livre da amostra. Comparar a posição com o ping recebido no original e confirmar ausência de duplicação. Testar após alterar tamanho, junto a uma base e com uma janela modal aberta. Em replay deve continuar a aparecer a cruz turquesa e a indicação de diagnóstico, sem envio. Confirmar aceitação real antes de declarar paridade de input; botão direito, interações de veículos, zoom/foco completos e substituição permanecem pendentes. As secções abaixo registam as etapas anteriores.

## Cliques na amostra Gameface — percurso de diagnóstico

A amostra aceita mousedown apenas com handshake atual, geometria/tamanho nativos válidos, adaptador disponível, HUD visível, cursor nativo visível e ausência de janela modal. Reutiliza `SHOW_CURSOR`/`HIDE_CURSOR` e `GUI.mcursor().visible`, como o painel de marcas; não força cursor ou foco. O listener de captura verifica que o alvo pertence à imagem da amostra e que as coordenadas cabem no seu getBoundingClientRect. Só esse caso consome o evento. Botões DOM esquerdo/meio/direito são convertidos para os índices nativos 0/2/1.

`onSampleInput` é um segundo comando exclusivamente diagnóstico. O backend confirma propriedade da view, geração/protocolo, cursor real, dimensões clássicas, geometria e modal; converte a posição normalizada para MINIMAP_SIZE e devolve x/y local em pixels. Não chama `onMinimapClicked`, comandos de chat ou APIs de disparo. Guarda apenas a última posição clicada pelo utilizador por view, reiniciada em cada batalha. A cruz turquesa representa a confirmação do Python; a magenta continua a representar cliques feitos no original. Um único listener é removido em dispose/reload. Sem suporte às APIs DOM necessárias, não se ativa input.

Teste: com a build nova, mostrar o cursor com Ctrl esquerdo e clicar **na amostra** junto a cantos/centro. Deve aparecer a cruz turquesa e o texto `Gameface → Python`, com valores entre 0 e 210. Soltar Ctrl e confirmar que a amostra deixa de captar cliques; clicar fora dela deve manter o comportamento habitual. Abrir uma janela modal para confirmar bloqueio. Não esperar pings no original nesta etapa. Pode ser testado num replay, pois o comando diagnóstico não depende do plugin de pings. Confirmar no runtime real receção, escalas/DPI, foco e ausência de interferências; os testes DOM não comprovam estes pontos.

## Diagnóstico do input nativo e do tamanho

Etapa de observação antes de ligar input ao Gameface. Um nono hook, instalado apenas com tacticalDiagnostics ativo, acompanha `MinimapComponent.onMinimapClicked(x, y, buttonIdx, mapScaleIndex)`. Chama o original exatamente uma vez, antes da observação, preserva o resultado e deixa propagar falhas do próprio cliente. Falhas do diagnóstico são contidas. Não chama comandos, não reenvia cliques e não altera foco, teclas ou pointer-events.

O cliente clássico converte coordenadas lógicas por `MINIMAP_SIZE`, não pelo tamanho visual do mapa; a ponte usa essa constante importada, valida os limites e publica apenas o último clique, botão, índice e sequência. A cruz magenta é uma referência diagnóstica persistente até outro clique ou fim/troca de batalha, não é um ping nem guarda posições de veículos. A geometria Flash acrescenta opcionalmente o índice `currentSizeIndex` (0–5), mantendo leitura do formato antigo. Não se escreve AccountSettings.

Teste: no minimapa **original**, usar Ctrl esquerdo e o rato como habitualmente, clicar em pontos reconhecíveis e comparar a cruz magenta na amostra. Usar as teclas nativas de aumentar/diminuir e confirmar o índice de tamanho no texto do diagnóstico. Repetir os cliques após redimensionar: a posição normalizada deve coincidir. A amostra mantém 200rem; o índice mede o tamanho original, não redimensiona a amostra. Confirmar que cada clique produz apenas a ação nativa habitual, sem duplicação, e que a saída da batalha limpa a referência.

Em replay, `ClassicMinimapComponent._setupPlugins()` não instala o plugin `pinging`; o hook pode observar chamadas que o Flash ainda publique, mas ausência de chamadas/pings nesse contexto não prova falha. O teste completo de comandos exige batalha real. Cliques sobre veículos/bases podem seguir callbacks específicos e ainda não são cobertos. Mouseover, atalhos, foco e encaminhamento Gameface permanecem pendentes. Mira/contorno estratégico aguardam o teste de artilharia indicado pelo utilizador.

## Limites visuais da câmara estratégica

A ponte Flash lê o retângulo local `getRect(entry)` de uma única `StrategicCameraMinimapEntry` visível e transforma os quatro cantos com localToGlobal, preservando rotação e escala nativas. É o contorno dos limites visuais da entrada, ainda não uma prova de equivalência à área completa de visão. Só é consultado quando a entrada Python estratégica selecionada é válida. Varredura limitada a 4000 nós, sem cache de posições, retorno primitivo de quatro pares; ambiguidades, geometria vazia ou exceder o limite de procura devolvem vazio.

O backend valida quatro pontos finitos dentro de margens limitadas e área não nula. A amostra reutiliza um polígono SVG azul e recorta o exterior ao mapa. Ao ocultar/sair do modo, desaparece sem TTL. Confirmar no replay de artilharia o contorno contra o original, incluindo rotação, zoom e mira próxima das margens. Se não coincidir com o desenho nativo, esta etapa deve ser revista antes de considerar paridade. O minimapa original permanece ativo. Etiquetas, limites e destruídos continuam pendentes de confirmação explícita, tal como a mira/contorno estratégico.

## Ponto de mira da câmara estratégica

A entrada nativa `StrategicCameraEntry`/`personal` usa `makeStrategicCameraMatrix()`, cuja translação vem da aimMatrix do cliente. A amostra acompanha apenas essa posição com uma mira azul, sem calcular dispersão, trajetória ou impacto. Requer propriedade do jogador vivo, ID selecionado e confirmado no plugin, modo estratégico/arty, entrada ativa e matriz publicada. Trocas de modo, desativação, remoção e fim de batalha retiram a mira. Reutiliza hooks/callbacks existentes.

Testar replay de artilharia: entrar na vista estratégica, mover a mira e comparar o centro com o original; testar a vista alternativa de artilharia e voltar ao arcade. Não representa ainda o retângulo/área de visão, rotação/escala estratégica ou câmara de vídeo. A validação de etiquetas, limites e destruídos continua pendente, assim como esta nova mira.

## Etiquetas dos veículos

Acrescentado o nome apresentado pelo cliente (`VehicleArenaInfoVO.getDisplayedName()`) aos ícones publicados, via campo `vehicleLabel` do adaptador e `label` sanitizado. Não se transportam IDs ou o campo de nome de jogador. Máximo de 64 caracteres, sem caracteres de controlo; o JS usa apenas textContent e aplica nova limitação defensiva. Etiquetas usam cor de relação, sombra, largura limitada e reticências. À direita de 70% do mapa ficam voltadas para a esquerda. Mantêm o nó ao mover; são removidas com a entrada. A rotação do jogador aplica-se só ao SVG, nunca ao texto.

Confirmar legibilidade no replay, nomes traduzidos, mudança de lado junto à margem, remoção ao perder avistamento e aspeto dos destruídos. A amostra de 200rem pode continuar a ter sobreposições em grupos densos; não há ainda resolução de colisões, configuração de tamanho de letra ou modos Alt. A seta própria pode não ter etiqueta quando a entrada pessoal não fornece nome. Limites azuis e destruídos continuam a aguardar confirmação visual explícita.

## Limites de rotação do canhão

Direção da câmara arcade e remoção ao mudar de modo confirmadas pelo utilizador. A etapa seguinte acompanha `setYawLimit(left, right)` e `clearYawLimit` na entrada `ViewPointEntry`, sem novos hooks/timers. O cliente converte os limites da torre para graus e só os publica conforme os modos, tipo de veículo e opção `SHOW_SECTOR_ON_MAP`. O Flash aplica esses ângulos à orientação da entrada pessoal (a correção de 180° é própria do desenho do atlas); a amostra usa diretamente yaw mundial do casco + offset em graus.

Os dois raios azuis são recortados à borda, respeitando mapas retangulares. Requer jogador vivo e proprietário da entrada, matriz ativa e limites válidos; clear/removal/fim de batalha retiram-nos, sem persistência. Testar com replay de artilharia com rotação limitada, rodar o casco e comparar as direções com o original; alterar a opção nativa de setores e verificar remoção. Uma torre sem limites publicados não deve produzir raios. Não se inferem limites de outros veículos. Câmaras estratégica/vídeo e setores de visão continuam pendentes; os destruídos continuam sem confirmação visual explícita.

## Linha de direção da câmara arcade

Acrescentada a entrada `ArcadeCameraEntry`/`personal` aos oito hooks existentes. O cliente usa `makeArcadeCameraMatrix()` com translação do veículo e rotação da câmara; a ponte lê só o provider já publicado, sem consultar BigWorld. Requer jogador vivo/não observador, ownership nativo, ID da câmara arcade selecionado, entrada ativa e comando `showDirectionLine`. `hideDirectionLine`, troca de modo, remoção, ocultação do HUD e finalização retiram a linha. Não são criados timers ou comandos de input.

O raio segue o yaw nativo, com x normalizado pela largura mundial e z pela altura mundial; termina na interseção com a borda do mapa. A amostra usa uma linha SVG amarela reutilizada. Confirmar rotação norte/este/sul/oeste, câmara livre em arcade e redimensionamento; desativar a opção nativa de vetor e mudar para mira/estratégico para confirmar remoção conforme o original. Setores de visão/limites do canhão e câmaras estratégica/vídeo continuam pendentes. Esta etapa e os destruídos ainda aguardam confirmação visual explícita.

## Veículos destruídos publicados

Inimigos próximos e distantes confirmados no jogo. A etapa seguinte usa `destroyedMarkers` do mesmo plugin nativo, separados dos veículos vivos. `VehiclesPlugin.__setDestroyed()` mantém a entrada ativa e chama `setDead` apenas conforme as opções nativas; o callback de expiração desativa-a. O adaptador aceita somente entradas ativas, mortas, com sinal nativo de publicação e localização AOI/FAR; não lê matrizes de destroços ocultos, de localização indefinida ou em transição. Não conserva posições nem cria TTL.

A ponte envia `destroyedPoints` sem IDs/nomes, após handshake e geometria válida. A amostra usa o SVG próprio `destroyed`, cor da relação e opacidade de 50%, sem orientação de jogador. Confirmar os símbolos e a remoção contra o original no replay, incluindo a opção nativa de mostrar destruídos e o fim da batalha. Lost Contact continua ausente. Validação visual desta etapa pendente.

## Inimigos atualmente avistados

Correção após a captura do replay: o filtro inicial omitira inimigos distantes visíveis. `VehiclesPlugin.updatePositions()` publica essas entradas como FAR e mantém `isInAoI=True`; `_hideVehicle()` passa a UNDEFINED/false quando deixam de estar avistadas. O adaptador aceita agora AOI ou FAR apenas com esse sinal nativo verdadeiro para inimigos. Continua a rejeitar FAR/false, UNDEFINED, transições e destruídos antes de ler matrizes. O teste reproduz publicação distante e posterior ocultação sem retenção.

Impactos de artilharia confirmados pelo utilizador. A próxima etapa acrescenta `enemyPoints` à amostra, apenas após handshake e geometria válida. A origem continua a ser o adaptador nativo: entrada ativa, viva, sinal de avistamento nativo e localização AOI/FAR, verificados antes de ler a matriz. Transições, entradas ocultas e destruídas são excluídas; não há pesquisa de entidades ou retenção da última posição. O transporte remove IDs e nomes e limita os veículos a 64 slots.

Os ícones SVG da classe aparecem a vermelho. Confirmar no replay a posição, classe e remoção quando o inimigo deixa de estar avistado, morre ou desaparece da entrada publicada; testar também avançar/recuar no replay. A amostra não oferece Lost Contact, não mostra destruídos nesta etapa e mantém o minimapa original. A validação visual desta etapa está pendente.

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

O indicador de impacto inimigo usa outro símbolo: `ArtyHitDotMarkerUI`, no contentor `personal`, publicado por `EnemySPGShotPlugin`. A amostra acompanha essa matriz como ponto vermelho e remove-o quando o cliente elimina a entrada (duração nativa de 10 segundos). Não subscreve eventos de disparo nem calcula posições adicionais; respeita `SHOW_ARTY_HIT_ON_MAP`, pois só recebe entradas efetivamente criadas. Posição e remoção ainda carecem de confirmação visual.

Células a piscar confirmadas no jogo. Acrescentado `ArtyMarkerMinimapEntry`, mapeado pelo cliente de `SPG_AIM_AREA_SUBTYPE` em `AreaStaticMarkerPlugin`. Usa o contentor `equipments` e a matriz publicada, com os mesmos hooks existentes e remoção nativa. A amostra desenha uma mira laranja (+); não calcula dispersão, raio, previsão de impacto ou posições de artilharia inimiga. Confirmar posição e desaparecimento contra o marcador original num replay que contenha esse evento. Não inclui os efeitos de consumíveis de artilharia nem indicadores de disparos inimigos.

### Correção das células a piscar

O utilizador confirmou que as células piscavam no original mas faltavam na amostra. Essas animações usam `SimpleAttentionToFlashMinimapEntry`, separadamente dos marcadores estáticos descritos abaixo. A ponte Flash lê apenas animações atualmente visíveis e ainda em curso, limitada a 4000 nós e 32 células. Converte o centro dos limites visuais para o centro de uma célula da grelha 10×10; outras dimensões não são aceites.

A amostra mostra um quadrado amarelo com a largura e altura de uma célula. Reutiliza a amostragem existente, sem criar TTL, histórico ou comandos. Quando a animação desaparece ou termina, o destaque é removido no próximo frame amostrado. O log `Ping diagnostics: static=… visibleCellAnimations=…` ajuda a confirmar a leitura. Compilação e testes automatizados não substituem a confirmação visual: comparar posição, início e remoção num replay com células a piscar no original.

Círculos confirmados pelo utilizador. A etapa seguinte espelha as entradas `MarkAttentionEntryUI` e `MarkGoingToPositionEntryUI` no contentor `equipments`, publicadas por AreaStaticMarkerPlugin a partir das comunicações do cliente. As fontes auditadas são shared/minimap/plugins.py (`_LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME`, `__addStaticMarker`, `__delStaticMarker`) e settings.py. O segundo símbolo também é usado pelo waypoint nativo de pré-batalha; não se inventa uma distinção que o símbolo não fornece.

Reutiliza os oito hooks e o callback de amostragem existentes. Estado attack/idle/reply vem de setState. A duração pertence ao cliente: a amostra remove quando há setActive(false)/delEntry e não cria TTL, relógio ou animação própria. Limite de 32 entradas; payload apenas tipo/x/y/estado, sem remetente, texto ou ID. Exclui símbolos não auditados, incluindo UnspottedMarkerUI. O fim de batalha/dispose liberta todas as referências de matriz.

Na amostra: ! amarelo = atenção; > azul = destino/waypoint; R = resposta; idle usa menor opacidade. Confirmar posição e remoção contra o original num replay com comunicações gravadas. O plugin de envio por clique é desativado pelo cliente em replays; isto não impede que marcadores recebidos/gravados sejam publicados. Um replay sem esses eventos pode manter o contador a zero. Não há envio de comandos, resposta automática ou interceção de cliques. Pings sobre veículos/bases, áreas de artilharia e outros estados de comunicação continuam fora deste contrato parcial.
