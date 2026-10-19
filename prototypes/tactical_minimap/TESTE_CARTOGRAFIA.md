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
