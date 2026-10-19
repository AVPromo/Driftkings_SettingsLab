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
