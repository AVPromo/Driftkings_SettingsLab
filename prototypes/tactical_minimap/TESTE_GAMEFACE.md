# Etapa 3 — diagnóstico Gameface em batalha

## Objetivo e limites

Esta build inclui uma ponte diagnóstica opt-in ligada ao `RandomHUDView` já usado pelo projeto. Não desenha outro mapa nem oculta o nativo. O painel recebe apenas estado, contagem de entradas publicadas em AoI, nome da textura, limites e dimensões lógicas. Não recebe IDs, nomes ou posições de veículos. Lost Contact e o modo de substituição continuam bloqueados.

A flag `tacticalDiagnostics` é guardada pelo Settings/MinimapStore e pelos perfis existentes, com default **false**, tanto na forma legada como nos quatro ficheiros atuais. É uma opção técnica de teste, sem controlo no painel normal. Defaults Python e snapshot foram regenerados pelo script, não editados à mão.

## Como testar manualmente

1. Com o jogo fechado, instalar o WOTMOD compilado desta etapa em `<jogo>/mods/2.4.1.0/Driftkings.wotmod`. A build local está em `build/debug/beta/0.1.2-beta.4/Driftkings.wotmod`. Não foi instalada automaticamente.
2. Consultar `<jogo>/mods/configs/Driftkings/load.json` para identificar o perfil ativo. Os seletores EU e NA locais indicavam `default` durante esta sessão.
3. No ficheiro `<jogo>/mods/configs/Driftkings/<perfil>/minimap_enhancements/minimap.json`, acrescentar ou alterar **apenas** a propriedade `"tacticalDiagnostics": true`. Preservar as restantes definições e a sintaxe JSON. Se o componente ainda estiver no ficheiro legado `<perfil>/minimap_enhancements.json`, colocar ali a propriedade; o loader existente trata da migração.
4. Arrancar o cliente e entrar numa batalha aleatória ou num replay que utilize `RandomHUDView`. Outros HUDs/modos não são suportados nesta etapa. A disponibilidade em replay necessita confirmação no cliente.
5. Espera-se uma caixa de texto no topo central: `Tactical Minimap — diagnóstico | Vanilla preservado`. Deve passar de ligação pendente para ligação confirmada. O minimapa normal deve continuar a funcionar.
6. Confirmar que zoom, pings, cliques, TAB, ocultar HUD, saída da batalha e reentrada continuam normais. A informação só é atualizada em eventos de ciclo/visibilidade; não há polling de posições nem se promete uma contagem por frame.
7. Recolher `game.log` com as mensagens abaixo. Para desligar, repor `"tacticalDiagnostics": false` e reiniciar o cliente.

No NA, com o perfil atual, o caminho é `D:/Games/World_of_Tanks_NA/mods/configs/Driftkings/default/minimap_enhancements/minimap.json`. No EU, substituir a raiz por `D:/Games/World_of_Tanks_EU`. Não usar o ficheiro de defaults do repositório para ativar apenas um cliente de teste.

## Mensagens de diagnóstico

Logger: `Driftkings.TacticalMinimapProbe`.

- `Diagnostic bridge enabled for next RandomHUD battle`: hooks declarados para esta sessão.
- `Gameface diagnostic view loaded; awaiting handshake`: o view Wulf terminou de carregar.
- `Gameface diagnostic handshake confirmed (protocol 1); Vanilla unchanged`: JS enviou a confirmação e Python aceitou-a para a geração atual da batalha.
- `native-adapter-unavailable`: fonte/owner não aceite ou indisponível; não é sinal para desligar o minimapa original.
- `waiting-native`: o componente nativo ainda não foi capturado/carregado.

Se o recurso, o asset JS ou o handshake falhar, não há ocultação a reverter: o original nunca foi desligado. A criação de um view diagnóstico que falhe devolve None; este comportamento de exclusão de um filho foi confirmado em `ViewComponent._constructChild` no SRC. Nenhum handler emite pings ou comandos de combate.

## Ciclo de vida e proteção

São declarados três hooks apenas quando a flag está true no arranque: child components do HUD, populate e dispose do MinimapComponent. Usam o HookRegistry existente e preservam os originais. Os quatro eventos de batalha são subscritos por `on_event`, com ownership do componente atual. Não é criado um event bus paralelo.

A ponte usa referências fracas, remove o adapter na saída/recriação do minimapa e limpa views ao finalizar. O protocolo inclui uma geração por batalha; confirmações antigas, duplicadas ou de views já removidos são ignoradas. JS subscreve alterações do modelo/subviews, sem timers de polling, e remove callbacks/listeners/DOM em dispose. Nenhuma rotina de diagnóstico chama as_setVisible/as_setAlpha nem altera minimapMode.

## Validação realizada e pendente

- Build completa: 269 módulos Python e 185 assets; recurso R, JS, CSS, HTML e bridge pyc confirmados dentro do WOTMOD.
- Core: 57 testes em Python 2.7 e 3, incluindo falha de construção, recurso ausente, defaults desligados, handshake por geração e limpeza.
- Settings: 25 testes em cada Python. JS existente, preview e novo protocolo passam; lint ES5 e sintaxe verificados. Defaults/catálogos continuam sincronizados.
- Não foi efetuada instalação, abertura do jogo ou teste real desta ponte. Nenhuma confirmação in-game é presumida.
- Os dois testes do instalador anteriormente identificados continuam fora desta etapa; não foram alterados para contornar as imagens locais das fixtures.

## Confirmação no cliente NA — 19-10-2026

O game.log confirma carregamento do view e handshake aceite em duas sessões de replay: 01:34:17.566 e 01:36:08.960 (hora local registada). O utilizador confirmou o texto diagnóstico e o funcionamento das restantes funções do minimapa. Não foram encontrados erros do TacticalMinimapProbe nestas sessões.

Isto confirma a ponte no replay NA testado, não valida todos os mapas/modos, desempenho ou substituição do renderer. O log não confirma, por si só, a disponibilidade completa dos dados nativos nem a contagem apresentada.

Foi também identificado um erro independente no view de marcas de excelência: a extensão de `_getEvents()` devolvia um comando e um handler soltos, em vez de uma sequência de pares. A vírgula em falta foi corrigida e foi acrescentada uma verificação portátil deste contrato. A ausência desse erro no cliente precisa de novo teste com o WOTMOD recompilado.
