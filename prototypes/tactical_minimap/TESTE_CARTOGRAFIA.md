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
