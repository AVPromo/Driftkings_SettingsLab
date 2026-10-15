# Revisão e plano de reorganização — Driftkings

Atualizado em 2026-10-15. Este documento regista as prioridades acordadas e deve
ser consultado antes de iniciar a próxima fase. A comparação foi guardada a pedido
do utilizador. A unificação dos defaults e nomes está concluída localmente. As fases 1 e 2 da
reorganização foram implementadas e validadas localmente; teste em jogo no fim.
Antes do ponto 2, o utilizador pediu a substituição da arquitetura antiga de
ConfigInterface/TemplateBuilder; consultar [análise das configurações](#organização-das-configurações--direção-da-refatoração).
Também foi analisada a organização de Flash/Gameface da referência; consultar
[análise das interfaces](#flash-e-gameface--análise-de-organização) ao refatorar o carregamento
de vistas e recursos. A reorganização específica das interfaces Flash/Gameface continua pendente.
Foi também guardada a [auditoria dos hooks](#auditoria-de-hooks-e-overrides): priorizar a
consolidação dos produtores de eventos de batalha e remover a sobreposição com
as pontes antigas durante esta refatoração. A primeira consolidação foi implementada na fase 2; consultar o estado abaixo.

## Contexto e decisões a preservar

- Projeto de modding para World of Tanks WG, regiões EU, NA e ASIA.
- As configurações fornecidas pelo utilizador são os defaults do modpack. A origem
  foi `D:\Games\World_of_Tanks_NA\mods\configs\Driftkings`; a cópia de distribuição
  está em `res/configs/Driftkings`. São configurações pessoais do mod, não do jogo.
- As traduções estão centralizadas em `Driftkings/i18n`: `TEXT` para módulos e
  `PANEL` para o painel, num ficheiro por idioma. Os 18 idiomas têm as 909 chaves
  dos módulos e 160 do painel; as adições automáticas precisam de revisão linguística.
- As imagens do carrossel devem ser lidas dos recursos montados no `.wotmod`.
- O compilador suporta Python 2.7, Flash, versão do mod e canais beta/stable.
- Os testes e a pasta `build/` ficam locais e não são enviados para o GitHub.
- A base anterior à reorganização foi `8aeaddadf02bd97154c9ee37525c0f36aeccb3e7`.
  A fase 1 foi enviada em `02d2fc2`. Os commits de cada etapa ficam na branch
  `main` de `https://github.com/dkruben/Driftkings_SettingsLab`.
- Ainda temos de definir como serão atualizados os modpacks. O commit/push anterior
  não publicou uma release nem distribuiu uma atualização aos utilizadores.

## Comparação de referência

Referência: https://github.com/Armagomen/battle_observer

Commit analisado: `4c01dd5b11ec8f44dfdc78e4d5cccd1bad1b2966`.
A comparação baseou-se na leitura do código, sem executar o Battle Observer.
Não existem medições comparativas de desempenho. A cópia local de consulta está
em `build/references/battle_observer`, excluída do Git.

O Battle Observer oferece exemplos úteis de serviços partilhados e regras
centralizadas de seleção das vistas por modo de batalha, SPG e presença de XVM.
O nosso projeto já tem mecanismos de ciclo de vida, capacidades de batalha,
compatibilidade, configuração e atualização que devem ser consolidados.

## Prioridades para a próxima fase

### 1. Unificar os defaults

**Concluído em 2026-10-15 e enviado no commit `02d2fc2`, juntamente com a fase 1.**

- `build_tools/generate_defaults.py` gera `settings/default_values.py` a partir
  dos JSON canónicos. `settings_data.py` mantém metadados e os accessors, sem os
  antigos valores manuais. Os atalhos também usam os valores dos JSON.
- O compilador gera o fallback diretamente no staging, sem alterar os fontes,
  e verifica os 33 componentes do pacote em Python 2.7 contra os JSON.
- Foram preservados os 48 ficheiros de defaults fornecidos pelo utilizador.
  A minimapa usa os quatro documentos atuais; o JSON antigo permanece como
  entrada de distribuição legada e não se sobrepõe aos documentos atuais.
- Evidência: 21 testes locais passaram, incluindo a preservação de um ficheiro
  de utilizador existente, alterações ao JSON e validação dos formatos divididos.
  Build protegida `0.1.2-beta.1` concluída; verificação dos defaults dos 33 módulos
  passou. Falta confirmar o comportamento em jogo com o novo pacote.
- Para editar defaults: alterar os JSON e executar
  `python build_tools/generate_defaults.py --write --refresh-snapshot`.

Objetivos tratados:

Extensão autorizada pelo utilizador: remover o segundo identificador interno.
As classes de configuração usam apenas `NAME`, com nomes de secção como
`arcade_zoom`. O gestor central, os templates, os defaults e os catálogos i18n
usam essas mesmas chaves. Os JSON mantêm-se separados. Os nomes antigos existem
apenas na adaptação de compatibilidade para preservar configurações, traduções,
caches e preferências do painel já guardadas.

- Usar os defaults do utilizador em `res/configs/Driftkings` como fonte canónica.
- Gerar ou verificar os fallbacks Python durante a compilação, evitando manter
  valores independentes em `settings/settings_data.py`.
- Divergência histórica corrigida nesta fase: `default/arcade_zoom.json` define `max=400`, `min=10`,
  `enabled=true`; o fallback Python antigo definia `max=160`, `min=4`, `enabled=false`.
- Preservar as configurações existentes de cada utilizador durante atualizações.

### 2. Compatibilidade e modos de batalha

- Corrigir `FEATURES['player_panel_pro']` em `core/mod_compatibility.py`: `('XVM')`
  é uma string; a coleção de um elemento deve ser `('XVM',)`.
- A integração `BattleObserver` é referida nos conflitos da minimapa, mas falta
  no mapa `MODULES`; a deteção fica em `UNKNOWN` e não produz o aviso esperado.
- Avaliar sobreposições de painéis, minimapa, relógios e Sexto Sentido, distinguindo
  presença de outro mod de conflito funcional confirmado.
- Tornar uniforme a utilização de `BattleCapabilities`, com regras explícitas
  para Random, Comp7, Frontline, eventos, replay e SPG.
- Evitar desativar indiscriminadamente funcionalidades apenas por detetar outro mod.

### 3. Dependências e diagnóstico de inicialização

- `Core.start()` regista falhas dos serviços, mas continua a iniciar os módulos.
  Declarar dependências e impedir a ativação de componentes sem os serviços necessários.
- Garantir limpeza das subscrições, callbacks e hooks quando há inicialização parcial.
- Registar sempre o resumo da inicialização: versões do jogo/mod, região, módulos
  ativos/desativados, falhas e motivos. Atualmente o resumo só aparece quando há falhas.
- Concentrar adaptações a mudanças de API do jogo para reduzir correções dispersas.

### 4. Definir a atualização completa do modpack

Esta fase continua pendente; não tratar o mecanismo de distribuição como concluído.

Comparação adicional do updater do Battle Observer (mesmo commit de referência):
consulta releases do GitHub ao entrar no login/garagem, com intervalo de duas
horas; mostra as notas da release e oferece atualização automática ou instalador
manual. Descarrega um ZIP, extrai ficheiros ainda inexistentes na pasta versionada
e lança um executável externo de limpeza das versões antigas ao finalizar.
Esta descrição resulta da leitura do código, sem execução do fluxo.

Aproveitar a apresentação clara da versão, notas e alternativa manual, e avaliar
um instalador inicial com seleção de componentes. A seleção deve corresponder ao
inventário real de instalação e às dependências declaradas pelo compilador.
O nosso updater já tem canais, compatibilidade com o jogo, SHA-256 e preparação
de instalação/recuperação; conservar essas bases. O manifesto atual descreve um
único `.wotmod`, pelo que ainda precisa de abranger a distribuição completa.
Não adotar a comparação exclusivamente numérica das versões, a extração sem
verificação explícita de hashes nem a limpeza transversal de pastas antigas.
Qualquer remoção deve depender do inventário de propriedade e preservar os
perfis/configurações. A aplicação após sair do jogo deve ser validada com o nosso
helper, em vez de introduzir outro executável descarregado de um ramo mutável.

- Definir um manifesto que identifique todos os ficheiros pertencentes ao modpack,
  respetivas versões, hashes, dependências e compatibilidade com a versão do jogo.
- Fechar as regras dos canais beta/stable e a promoção de uma versão entre canais.
- Separar atualização do código, dependências e defaults; preservar perfis,
  configurações e alterações pessoais dos utilizadores.
- Determinar quais os ficheiros antigos que podem ser removidos, com base no
  inventário do modpack, sem afetar outros mods instalados.
- Fechar instalação após sair do jogo, recuperação em caso de falha, reinício e
  apresentação do resultado. Já existem bases de validação SHA-256 e rollback;
  confirmar o comportamento completo antes de publicar.
- Rever a limitação de endurecimento de `WindowsFiles` registada no README.
- Validar o fluxo completo em ambiente local antes da primeira distribuição.

### 5. Medir e otimizar as interfaces

- Medir custos de callbacks e chamadas Python → Flash/Gameface antes de otimizar.
- Evitar enviar propriedades inalteradas e agrupar alterações quando apropriado.
- Reutilizar dados partilhados e atualizações por eventos, verificando a limpeza
  dos listeners e timers na saída de cada vista/contexto.
- Não afirmar melhorias de FPS sem medições comparáveis.

## Como retomar

Consultar este plano e confirmar o estado atual dos ficheiros antes de editar.
Seguir a ordem acima, salvo nova orientação do utilizador. Manter a definição da
atualização do modpack como trabalho pendente até existir validação completa.
Atualizar este documento à medida que cada prioridade for concluída, com evidência
do que foi verificado e do que continua por validar.

## Plano de reorganização por fases

Este é o documento único de referência. As análises detalhadas seguem depois
deste plano; não constituem alterações de runtime já executadas.

### Fase 0 — Preservar a base concluída

- Manter os 48 JSON pessoais como defaults canónicos e os JSON separados.
- Preservar as 33 secções com NAME, sem reintroduzir ID, e a geração dos fallbacks.
- Manter os 18 catálogos i18n unificados; rever linguisticamente as traduções automáticas.
- Preservar as correções de recarga com C, Safe Shot, Sexto Sentido, visibilidade,
  imports circulares e carregamento duplicado de bancos de som.
- Registar a build de referência e confirmar em jogo as alterações locais de defaults/nomes.

### Fase 1 — Substituir a arquitetura das configurações

**Implementada e validada localmente em 2026-10-15; validação em jogo reservada para o fim.**

- Removidos ConfigInterface, ConfigNoInterface, ConfigBase, SettingsLifecycle,
  TemplateBuilder, fachadas antigas, scanner/IO sem consumidores e registo adiado do painel.
- `settings/definitions` substitui `settings/templates`: mantém declarações e
  normalizações específicas, sem construir templates nem possuir o ciclo de persistência.
- `settings/service.py` gere inicialização, leitura, aplicação e gravação de candidatos.
  Os atalhos são convertidos numa cópia para persistir, sem alterar o dicionário ativo.
- `controls_schema.py` declara metadados; `registry.py` resolve controlos diretamente,
  e `panel/sections.py` liga-os ao painel Gameface sem o antigo TemplateAdapter.
- Migrados os casos específicos de PlayerPanelPro, minimapa, carrossel, relógio e gunmarks.
  Mantidos os JSON separados, formatos de armazenamento e identidades persistidas do painel.
- Os dicionários aninhados mantêm as referências durante aplicação e recarga.
- Corrigida a interpolação de um tooltip de cor com texto UTF-8 em Python 2.7 e a
  importação de MinimapStore no caminho de migração a partir do ficheiro único.
- Comparação local antes/depois: 32 secções e 684 controlos com mesmos valores,
  defaults, opções, limites e traduções; retirado apenas o valor duplicado que o builder
  incluía nos metadados. O carrossel foi excluído desta comparação e não foram recriados
  os seus testes removidos a pedido do utilizador.
- Verificação: 21 testes existentes e 7 testes de integração em Python 2.7, incluindo
  ligação das 32 secções ao painel nos 18 idiomas, perfis, atalhos, reset, referências,
  falha de escrita e preservação dos ficheiros pessoais. APIs do jogo simuladas.
- Build protegida `0.1.2-beta.1` concluída: 251 módulos Python; Flash, ponte do
  carrossel e helpers recompilados. Defaults dos 33 componentes verificados no pacote.
- Pacote local: `build/releases/beta/0.1.2-beta.1/Driftkings.wotmod`.
- Limites: não foi instalado no jogo nem publicada uma release. A instanciação durante
  os imports dos módulos e o bootstrap de common pertencem à fase 2 e continuam ativos.

Trabalho previsto e agora migrado:

1. Inventariar opções, tipos, limites, ações, previews, atalhos e formatos de cada secção.
2. Tornar o gestor central proprietário da carga, validação, perfis, gravação e notificações.
3. Migrar comportamentos especiais do carrossel, PlayerPanelPro, minimapa e gunmarks.
4. Declarar metadados do painel diretamente para o modelo Gameface existente.
5. Migrar todos os consumidores e remover ConfigInterface, ConfigNoInterface,
   TemplateBuilder, as suas reexportações e o adaptador antigo.

Aceitação: mesmas opções e limites, apply/reset/perfis/atalhos funcionais,
referências aos dados preservadas e ficheiros pessoais sem alterações involuntárias.
A compatibilidade com nomes persistidos antigos fica apenas nas fronteiras de leitura.

### Fase 2 — Unificar arranque, serviços e eventos

**Implementada e validada localmente em 2026-10-15; teste em jogo no fim.**

- A entrada `mod_Driftkings.py` importa/cria o Core apenas em `init()`, com suporte
  explícito EU/NA/ASIA e `init()`/`fini()` idempotentes.
- O construtor do Core guarda fábricas de serviços; a criação e o arranque ocorrem
  em fases explícitas, primeiro a base e depois as interfaces/updater.
- `ServiceSpec` declara dependências. Serviços dependentes ficam bloqueados quando
  uma dependência falha; componentes sem serviços obrigatórios não são ativados.
- O perfil é validado antes dos consumidores. Componentes com falha são retirados
  dos contextos e das entradas de configuração pertencentes ao seu proprietário.
- Removidos o bootstrap de common, callbacks de hooks durante imports e aliases
  adiados. Os hooks de notificações foram preservados num serviço explícito;
  helpers de diálogos sem consumidores foram removidos.
- Há um único produtor por alvo de startGUI, destroyGUI, saúde, aparência,
  feedback de batalha e populate de login/hangar. Os consumidores usam eventos;
  a limpeza de gunmarks, mira e movimento continua antes do destroy nativo.
- Saúde dispõe de sinais completos antes/depois, além do sinal reduzido existente.
  São preservados veículo, HP novo/anterior, atacante e motivo.
- `HookRegistry` identifica alvo/handler/proprietário, instala cada declaração uma
  vez e gere a ligação/desligação das subscrições. Importações falhadas abandonam
  as suas declarações. Wrappers desativados encaminham para o original; não se
  repõe cegamente um método que outro mod possa ter envolvido posteriormente.
- Contextos, teclado, vistas e serviços fazem limpeza de arranque parcial; os
  callbacks de cada componente são cancelados na sua desativação.
- O resumo de arranque usa o log nativo, incluindo versões, região, componentes,
  estado dos serviços, falhas e motivos de bloqueio, mesmo sem erros.
- Contagem estática: 186 → 162 pontos de instalação, 42 → 37 ficheiros. Os
  alvos acima têm um produtor cada. Não é medição de hooks simultâneos nem de FPS.
- Verificação local: 21 testes existentes, 7 de configurações e 17 novos de Core,
  ownership e produtores de eventos, em Python 2.7 com APIs do jogo simuladas.
  Inclui método nativo chamado uma vez, argumentos/retornos/exceções, falhas
  parciais, ciclos de batalha, 20 reativações e preservação de um wrapper externo.
- Build protegida `0.1.2-beta.1`: 248 módulos Python, 169 assets, 48 defaults,
  duas dependências; Flash, ponte do carrossel e helpers recompilados.
- Os hooks de handleKey foram avaliados e conservados: a recarga precisa da
  execução nativa anterior e observar a tecla no KeyboardService não demonstra
  aceitação do comando. A sua remoção exige contrato equivalente validado.
- Limites: permanecem wrappers inativos na cadeia, por compatibilidade com outros
  mods. A reorganização de recursos/vistas pertence à fase 3; o teste real no jogo
  continua reservado para o fim. Não foi instalada nem publicada uma release.

Objetivos desta fase:

- Criar os serviços em init(), eliminando bootstrap e instanciação durante imports.
- Definir ordem, dependências obrigatórias, falhas isoladas e um proprietário da limpeza.
- Consolidar start/destroy de batalha, saúde, aparência, feedback e entrada no hangar.
- Migrar consumidores dos hooks duplicados para eventos com argumentos e ordem equivalentes.
- Unificar o registo de hooks, impedir instalações duplicadas e preservar cadeias de outros mods.
- Registar resumo de arranque, módulos ativos/inativos e motivos, mesmo sem falhas.

Aceitação: entrada/saída repetida de batalha e hangar sem acumulação de handlers;
falha parcial não ativa consumidores sem dependências nem impede limpeza.

### Fase 3 — Organizar interfaces e recursos

- Catálogo central de vistas: aliases técnicos, classes Python/AS3, recursos, modos e lifecycle.
- Manter um SWF de batalha, classes por funcionalidade e bases/utilitários partilhados.
- Delimitar fábricas de batalha e ratings; validar o contrato nativo antes de alterar registos.
- Agrupar Gameface por funcionalidade com modelo Python, recurso R e HTML/CSS/JS identificáveis.
- Simplificar a injeção só quando ordem, recuperação, cancelamento e dispose estiverem preservados.
- Isolar a ponte do carrossel e manter validação do patch por versão; ícones dentro do .wotmod.
- Atualizar caminhos, manifests de build e recursos em conjunto.

Aceitação: build recompila AS3; vistas criam uma vez, redimensionam e libertam recursos;
visibilidade, ratings, carrossel e painel continuam funcionais em jogo.

### Fase 4 — Compatibilidade e adaptação ao jogo

- Corrigir a coleção XVM de um elemento e completar a deteção BattleObserver.
- Centralizar capacidades/regras de Random, Comp7, Frontline, eventos, replay e SPG.
- Distinguir presença de outro mod de conflito funcional e limitar desativações ao necessário.
- Concentrar adaptações das APIs WG para facilitar futuras mudanças do cliente.

Aceitação: motivos de ativação/desativação explícitos e validação dos contextos suportados.

### Fase 5 — Fechar instalação e atualização do modpack

- Expandir o manifesto de um .wotmod para inventário completo de componentes e dependências.
- Ligar versão/canal/compatibilidade/hashes aos artefactos emitidos pelo compilador.
- Separar código, dependências e defaults; preservar perfis e personalizações.
- Mostrar versão, notas, progresso, resultado e alternativa de instalação manual.
- Remover ficheiros antigos apenas quando pertencem ao inventário Driftkings.
- Validar instalação após fechar o jogo, recuperação de falhas e resultado no arranque seguinte.
- Definir promoção beta/stable e processo de publicação antes da primeira release.

Aceitação: fluxo completo local, incluindo falha e recuperação, sem afetar outros mods
ou configurações pessoais. A existência de helpers não equivale a distribuição validada.

### Fase 6 — Medir, otimizar e estabilizar

- Medir callbacks, frequência de hooks e tráfego Python → Flash/Gameface.
- Evitar propriedades inalteradas, agrupar atualizações e reutilizar dados partilhados.
- Rever caches de estatísticas e informação de veículos sem duplicar serviços existentes.
- Executar regressão funcional e build protegida em Python 2.7, Flash e Gameface.

Aceitação: evidência de preservação funcional e medições antes/depois quando se alegam ganhos.
Não existe objetivo de igualar a contagem de hooks do Battle Observer.

### Estrutura de responsabilidades proposta

```text
mod/res/scripts/client/gui/mods/mod_Driftkings.py  entrada e lifecycle explícitos
mod/res/scripts/client/Driftkings/
  _constants.py       nomes, chaves e contratos partilhados
  core/               composição, serviços, eventos, compatibilidade e updater
  settings/           dados, gestor, persistência, perfis e metadados declarativos
  settings/panel/     ligação direta dos metadados ao painel Gameface
  battle/ e lobby/    comportamento dos módulos, consumidores dos serviços
  views/ e meta/      vistas Python e contratos de comunicação
  i18n/               traduções dos módulos e painel por idioma
flash_source/         fábrica, bases, componentes e utilitários AS3
mod/res/gui/          recursos Flash/Gameface e registos de layouts
res/configs/          defaults pessoais canónicos de distribuição
build_data/           contrato de entrada, dependências e patches por versão
build_tools/          geração, compilação, empacotamento e preparação da publicação
```

A árvore descreve responsabilidades e aproveita a estrutura existente; os caminhos
finais de novos módulos serão fixados ao migrar os seus consumidores.

### Regras de execução

- Próximo trabalho: fase 3, organização de interfaces e recursos. Por indicação do utilizador,
  a validação em jogo será realizada apenas no fim da reorganização.
- Migrar por conjuntos funcionais verificáveis; remover a camada obsoleta quando os seus
  consumidores estiverem migrados, sem manter uma segunda arquitetura permanente.
- Testes, referências e build ficam locais; não publicar releases durante a reorganização.
- Atualizar este documento com o estado e evidências de cada fase. O utilizador
  autorizou commit e push no fim de cada etapa; executar após as verificações locais,
  mantendo testes e build fora do GitHub. Não é necessário repetir o pedido de autorização.
- A validação em jogo fica para o fim, por indicação do utilizador. Commit/push não
  publica uma release nem instala o mod no jogo.

## Análises detalhadas consolidadas


## Organização das configurações — direção da refatoração

Pedido do utilizador em 2026-10-15: seguir a organização de responsabilidades do
Battle Observer e retirar o antigo sistema ConfigInterface/TemplateBuilder.
A análise abaixo regista a situação inicial. A substituição foi implementada
localmente nesta sessão; consultar o estado da fase 1 para a validação.

### O que o Battle Observer faz

Referência analisada: Armagomen/battle_observer,
commit `4c01dd5b11ec8f44dfdc78e4d5cccd1bad1b2966`.

- `armagomen/_constants.py` declara nomes de secções, chaves das opções,
  enumerações, listas de carregamento, relações entre opções e aliases das vistas.
  Usa classes e namedtuples; o benefício principal é a centralização dessas chaves.
- `settings/settings_data.py` guarda os dicionários por secção num único objeto.
- `settings/settings_loader.py` carrega os JSON, mantém o estado partilhado e
  expõe `getComponentDict`, `getSetting` e `setSetting`.
- `settings/interface.py` declara o contrato do serviço. O registo do serviço
  usa o gestor de dependências do jogo e um finalizador.
- Os módulos usam o serviço e as constantes diretamente. Exemplo observado:
  `settingsLoader.getSetting(CREW.NAME, CREW.RETURN)`.
- `settings/hangar` trata da construção e das ações do painel. Percorre os
  valores e caminhos aninhados e aplica fábricas de controlos, traduções e
  exceções declaradas. Existe construção de templates (`CreateElement`,
  `getTemplate`), mas não a nossa cadeia de ConfigInterface/TemplateBuilder.
- O painel dele depende de vxSettingsApi. O nosso painel Gameface continua a
  ser o destino; essa dependência não faz parte da migração.

Um detalhe que exige decisão explícita: o `getSetting` dele combina valores
booleanos com o `enabled` da secção. O nosso gestor devolve o valor da opção.
Preservar o comportamento atual durante a migração; regras de ativação devem ser
explícitas e não surgir como efeito indireto da troca de arquitetura.

### Estado atual do Driftkings

#### Entrada do jogo e arranque dos serviços

Também analisado a pedido do utilizador:
`mod/res/scripts/client/gui/mods/mod_armagomen_battle_observer.py`.

O ficheiro é a entrada reconhecida pelo carregador de mods do jogo. Contém
metadados e um `init()` que verifica a região, regista o logger e regista o Core
e o updater no gestor de dependências do jogo com `finalizer='fini'`. Os restantes
callbacks declarados são operações vazias; a limpeza dos serviços é delegada aos
finalizadores registados. A versão analisada exclui explicitamente RU; isso não
é uma lista explícita de certificação de todas as outras regiões.

O Core dele regista primeiro as configurações, depois os serviços partilhados,
carrega os componentes, regista as vistas e prepara o painel. A entrada não
contém lógica de funcionalidades nem constrói configurações de cada módulo.

Diferenças concretas no nosso projeto:

- `gui/mods/mod_Driftkings.py` já é uma entrada pequena e tem `init()`/`fini()`,
  mas constrói `Core()` ao importar o ficheiro, antes de chamar `init()`.
- O construtor do nosso Core importa e instancia vários serviços. O ciclo de
  vida explícito está parcialmente antecipado para a fase de importação.
- `common/__init__.py` ainda chama o bootstrap e o carregamento de imports
  adiados durante a importação. Isso cria outro caminho de inicialização a
  eliminar ao substituir a camada antiga.

Direção para a refatoração: importar/criar os serviços dentro do arranque explícito,
inicializar o gestor de configurações antes dos consumidores e ter um único
proprietário da limpeza. Confirmar idempotência, ordem e falhas parciais. Se for
usado o gestor de dependências WG, verificar a sua ordem de finalização; não
misturar finalizadores desse gestor com uma segunda limpeza independente.
Preservar a lista explícita de suporte EU/NA/ASIA e a fonte única da versão no
compilador. O logger deve pertencer ao Driftkings: o exemplo chama
`logging.disable(...)` globalmente, o que pode afetar o diagnóstico do cliente
e de outros mods. Essa chamada não deve ser reproduzida.

Fluxo pretendido:

```text
gui/mods/mod_Driftkings.py:init()
  → logging do Driftkings
  → gestor de configurações e dados centrais
  → serviços partilhados
  → módulos de batalha/hangar
  → vistas e painel Gameface
  → serviço de atualização, com contexto seguro
```

`fini()` ou os finalizadores do proprietário escolhido libertam os recursos
na ordem adequada, incluindo subscrições, callbacks e hooks. Este fluxo é a
direção proposta; a implementação do arranque atual ainda não foi alterada.

Já concluído: nomes canónicos das secções, defaults gerados dos JSON, catálogos
i18n com as mesmas chaves, acesso central e adaptação dos nomes antigos para
dados persistidos. Os JSON permanecem separados e são a fonte dos defaults.

Cadeia encontrada na revisão inicial e entretanto removida:

`settings/templates/base.py` → `DriftkingsConfigInterface` → `ConfigInterface`
→ `ConfigBase` / `SettingsLifecycle` → `TemplateBuilder`.

Na revisão inicial, o arranque dependia da instanciação das classes de configuração
de cada módulo, de registos realizados nesse ciclo e de um adaptador de templates
no painel. A remoção de `ID`, por si só, não retirava essa cadeia; a fase 1 removeu-a.

### Destino da refatoração

1. `_constants.py`: nomes e chaves partilhados; sem persistência, construção de
   painel ou inicialização de módulos. Manter limites/metadados no proprietário
   adequado, sem transformar este ficheiro num controlador.
2. Dados: uma coleção central com as 33 secções, inicializada a partir dos
   defaults gerados. As referências dos dicionários devem sobreviver a reload/apply.
3. Gestor: proprietário único da carga, validação, gravação, notificações,
   seleção de perfis e aplicação. Inicialização explícita pelo Core.
4. Controladores: consulta do gestor por `SECTION.NAME` e pelas chaves das opções;
   subscrições de alterações com limpeza explícita. Sem possuir ConfigInterface.
5. Metadados do painel: declarações de etiquetas, tipos, limites, opções,
   dependências e previews por secção. Os valores vêm do gestor. Preservar os
   limites existentes; não os adivinhar a partir de valores numéricos.
6. Painel: gerar diretamente os controlos do nosso modelo Gameface a partir dos
   metadados e dos dados centrais. Substituir o adaptador da antiga interface.
7. Compatibilidade: nomes antigos apenas na leitura de dados e identidades
   persistidas. Essa adaptação não deve manter a arquitetura antiga em execução.

### Remoção e verificação

- Mapear todos os imports de ConfigInterface, ConfigNoInterface e TemplateBuilder,
  incluindo reexportações em `common/config` e imports implícitos em `common`.
- Migrar os hooks de aplicação específicos e os formatos divididos de carrossel,
  PlayerPanelPro e minimapa para os proprietários explícitos do novo gestor.
- Migrar atalhos e respetiva subscrição/limpeza para serviços do Core.
- Substituir `settings/templates`, `template_schema`, `template_builder`,
  `config_interfaces` e o adaptador antigo pelas declarações e ligação nativas.
- Remover os ficheiros obsoletos e as suas reexportações depois de migrar os
  consumidores. Não deixar fachadas antigas a suportar os módulos migrados.
- Validar os 33 módulos, 18 idiomas, opções e limites, defaults/reset, atalhos,
  perfis, formatos divididos, notificações e temporização das alterações.
- Comparar antes/depois a descrição dos controlos e a preservação dos ficheiros
  do utilizador. Executar compilação e verificação em Python 2.7 e testar em jogo.
- Manter testes e artefactos de build locais, conforme instrução do utilizador.

Esta etapa foi implementada localmente; a confirmação em jogo será feita no fim,
por indicação do utilizador. A atualização completa do
modpack continua pendente e não deve ser publicada durante esta refatoração.

## Flash e Gameface — análise de organização

Análise pedida pelo utilizador em 2026-10-15. Referência:
Armagomen/battle_observer, commit `4c01dd5b11ec8f44dfdc78e4d5cccd1bad1b2966`.
Leitura de código; o Battle Observer não foi executado. Nenhuma alteração ao
runtime foi feita nesta análise.

### Flash de batalha

O Core declara `modBattleObserver.swf` em `BATTLE_REQUIRED_LIBRARIES` e associa
o pacote Python de batalha aos modos através de `battlePackages`. A biblioteca
é carregada no contexto da UI nativa; não é uma janela independente.

O pacote Python `battle/__init__.py` contém `getViewSettings()` com o mapa
alias → classe Python e um `PackageBusinessHandler`. O serviço `IViewSettings`
seleciona os componentes ativos com base nas configurações, modo e conflitos;
também associa vistas aos controladores de sessão quando necessário.

Quando a página surge, o handler procura a vista e espera pela fábrica Flash.
O limite observado é de 80 tentativas, espaçadas por 0,1 segundos. Depois chama
`as_BattleObserverCreate` com os aliases escolhidos.

Em AS3, `BattleObserverLibraryMain` instala essa fábrica em
`BaseBattlePage.prototype`, mapeia os aliases para classes visuais e cria os
componentes. Evita registos duplicados, chama `registerComponent`, repõe o timer
pré-batalha na ordem visual e atualiza as dimensões do palco. A comunicação Python
↔ Flash usa DAAPI, com classes `meta/battle` e ciclo `_populate`/`_dispose`.

Organização observada:

```text
as/src/.../BattleObserverLibraryMain.as    fábrica única da biblioteca
as/src/.../battle/components/...          visuais AS3 por funcionalidade
scripts/client/.../battle/...             controladores Python das vistas
scripts/client/.../meta/battle/...        contrato DAAPI
scripts/client/.../shared/battle/...      seleção e serviços partilhados
```

### Quantidade, construção e organização dos SWF

O projeto Flash analisado declara uma única saída:
`mod/res/gui/flash/modBattleObserver.swf`. A entrada de compilação é
`BattleObserverLibraryMain.as`; as classes referenciadas são ligadas à mesma
biblioteca. Foram encontrados 38 ficheiros AS3 no projeto, não 38 SWF.
Não foi encontrado um segundo projeto Flash nem um binário SWF versionado na
cópia analisada; a conclusão refere-se à organização declarada nos fontes.

Os componentes ficam em `battle/components`, as bases em `battle/base` e os
utilitários partilhados em `utils`: texto, formatos, barras e animações. A base
`ObserverBattleDisplayable` concentra comportamento comum de interação, resize
e limpeza, sobre a classe BattleDisplayable do jogo. Cada componente mantém a
sua apresentação e os seus métodos DAAPI.

O `.as3proj` declara as bibliotecas WG como `externalLibraryPaths`, para compilar
contra os contratos do jogo. Não indica incorporação das classes WG através de
`includeLibraries`. Algumas imagens são incorporadas por `[Embed]`; outras, como
os ícones selecionáveis do Sexto Sentido, são carregadas de `gui/maps` em execução.
Um só SWF não implica que todas as imagens estejam dentro desse SWF: podem estar
como recursos separados dentro do mesmo `.wotmod`.

O projeto indica otimização, modo estrito, remoção de traces e SWF sem compressão;
declara 25 fps e alvo Flash Player 28. São opções do projeto de referência, não
uma recomendação automática para o nosso compilador ou uma medida de FPS do jogo.
Os scripts CMD analisados compilam Python e empacotam os ficheiros; não foi
identificada neles uma chamada que recompile o AS3 antes desse empacotamento.

O Driftkings já usa o mesmo princípio de biblioteca única (`DriftkingsBattle.swf`),
e o nosso compilador recompila-a a partir do AS3 antes de criar o pacote. Manter
essa integração. A melhoria é a organização e os contratos internos: um mapa
central de componentes, bases/utilitários partilhados, classes por funcionalidade
e lifecycle previsível. Separar os fontes não exige produzir um SWF por módulo.

### Gameface do hangar

`hangar_gf/__init__.py` liga a criação de componentes filhos ao
`LobbyHeader._initChildren`, com tratamento de cabeçalhos de modos especiais.
Remove o hook em `fini()`.

Cada funcionalidade tem um `ViewModel` e um `ViewComponent`. O modelo declara as
propriedades que o JavaScript observa. No `_initialize`, chama `gf_mod_inject`
com o alias e os CSS/JS próprios da vista. O componente define o recurso de layout
`R.mods...`, subscreve eventos ao carregar e remove subscrições/timers na finalização.

`gui/gen_resources/armagomen.battle_observer.json` associa cada recurso `R` ao
HTML e à entrada Gameface. Os HTML também referenciam CSS e módulos JS. O JS usa
`ModelObserver` e `MediaContext` disponibilizados pelo OpenWG, além de utilitários
próprios para DOM e posicionamento. O relógio analisado acrescenta o seu elemento
ao cabeçalho nativo quando o DOM necessário está disponível.

```text
scripts/client/.../hangar_gf/date_times.py modelo e ciclo de vida Python
gui/gen_resources/...json                R → HTML/entrada Gameface
gui/gameface/mods/.../hangar/clock/       clock.html + clock.css + clock.js
```

O carregamento é feito através de Wulf e OpenWG. Não é uma substituição global
dos bundles de produção do jogo. Isso não elimina a dependência de seletores DOM:
o relógio ainda procura elementos do cabeçalho através de seletores CSS.

### Comparação com o Driftkings

| Responsabilidade | Battle Observer | Driftkings atual |
| --- | --- | --- |
| Biblioteca de batalha | `modBattleObserver.swf` | `DriftkingsBattle.swf` |
| Catálogo Python/DAAPI | pacote battle + meta/battle | views/battle + meta/battle |
| Fábrica AS3 | instalada em BaseBattlePage | instalada em AbstractView, também usada pelas superfícies de ratings |
| Instanciação Flash | registerComponent | addChild + registerFlashComponentS, com visibilidade própria |
| Regras de seleção | serviço IViewSettings | capacidades e seleção de vistas existentes |
| Gameface | recursos diretos por modelo | attach_assets → AssetsModel → shared/bootstrap.js → recursos |
| Ciclo de limpeza JS | depende das bibliotecas e da funcionalidade | bootstrap gere carregamento, descarregamento e dispose dos owners |
| Carrossel | não foi identificado um equivalente à nossa ponte | patch do bundle nativo + recursos próprios |

### Direção para a organização futura

- Manter a separação entre Flash de batalha e Gameface de hangar/configuração.
- Ter um catálogo explícito para vistas e respetivos aliases, modos, recursos e
  ciclo de vida. Distinguir o nome da secção de configuração do alias técnico da UI.
- Concentrar a seleção de componentes de batalha num serviço, reutilizando as
  capacidades existentes, antes de pedir a criação dos visuais.
- Delimitar as fábricas Flash por tipo de página. Avaliar separar a fábrica dos
  ratings da fábrica de batalha; a extensão a AbstractView tem âmbito mais amplo.
- Verificar a compatibilidade de `registerComponent` com os nossos SWCs e a API
  do jogo antes de alterar o registo atual. É uma API protegida; tentativas locais
  anteriores de invocação indireta falharam. Não remover o encaminhamento atual
  de visibilidade apenas por copiar a chamada do projeto de referência.
- Avaliar injeção Gameface direta por vista para simplificar o bootstrap, mas
  preservar ordem de carregamento, módulos partilhados, recuperação de falhas,
  descarregamento e cancelamento de cargas tardias que ele gere hoje.
- Agrupar HTML/CSS/JS por funcionalidade e identificar claramente o modelo Python
  e o recurso `R` correspondente. Evitar reorganizar caminhos sem atualizar os
  manifests de build e os registos de recursos em conjunto.
- Manter a ponte específica do carrossel isolada, com validação por versão do jogo.
  O exemplo do hangar não prova que a ponte possa ser eliminada.
- Verificar a limpeza de timers, callbacks e observadores JS por vista; não
  presumir que uma organização mais curta garante limpeza ou melhor desempenho.

Esta análise integra a refatoração do arranque, configurações e organização das
interfaces descrita na análise das configurações deste documento. A distribuição de
atualizações do modpack continua como etapa posterior, ainda pendente.

## Auditoria de hooks e overrides

Análise estática em 2026-10-15. Referência: Battle Observer,
commit `4c01dd5b11ec8f44dfdc78e4d5cccd1bad1b2966`.
Não foram medidos FPS, tempos de frame ou cadeias ativas no cliente. Esta
auditoria regista o estado inicial; a consolidação posterior está descrita na fase 2.

### Inventário e limites

Foram percorridos os AST dos módulos Python do Driftkings e de `armagomen`.
Contaram-se chamadas explícitas a `override`, `overrideMethod`, variantes
estáticas/de classe e `toggleOverride`. Excluíram-se cancelamentos e chamadas
`toggleOverride(..., False)`, além de chamadas internas dos próprios helpers.
No Battle Observer, `factory.override(*args)` não é instalação de hook e foi
excluída. O ficheiro Python 2 `common/utils/abstract.py` não foi analisado pelo
parser Python 3; a leitura confirmou que trata de traceback e não instala hooks.

| Projeto | Pontos estáticos de instalação | Ficheiros com pontos de instalação |
| --- | ---: | ---: |
| Driftkings | 186 | 42 |
| Battle Observer | 31 | 14 |

Estes números não representam hooks ativos em simultâneo. Um ponto num ciclo
pode instalar vários hooks; condições podem instalar nenhum. O inventário não
cobre todas as formas possíveis de monkey patching, como `setattr` arbitrário,
atribuições diretas ou alterações de protótipos JavaScript/AS3. As funcionalidades
dos projetos também diferem; a diferença numérica não prova uma diferença de FPS.
O detalhe bruto local está em `build/hook_audit.json`.

### Redundâncias confirmadas no Driftkings

| Alvo normalizado | Instalações no código | Candidatura |
| --- | ---: | --- |
| PlayerAvatar.__startGUI | 8 | Centralizar o ciclo de entrada em batalha |
| PlayerAvatar.__destroyGUI | 9 | Centralizar a saída e a limpeza |
| Vehicle.onHealthChanged | 3 | Um produtor de eventos, vários consumidores |
| LoginView._populate | 3 | Centralizar a notificação de entrada na vista |
| PlayerAvatar.handleKey | 2 | Avaliar o serviço de teclado existente |
| PlayerAvatar.vehicle_onAppearanceReady | 2 | Partilhar o evento de aparência pronta |
| PlayerAvatar.onBattleEvents | 2 | Avaliar um serviço de feedback partilhado |

`core/battle_events.py` já instala hooks centrais e publica eventos. Alguns
consumidores usam-no, enquanto outros continuam a instalar hooks individuais
para os mesmos alvos. `common/utils/events/player_avatar.py` mantém ainda outro
encaminhamento antigo para startGUI/destroyGUI, instalado por callback durante
a importação. É uma duplicação de mecanismos de ciclo de vida.

Concentrações por ficheiro: `lobby/hangar_options.py` tem 24 pontos,
`battle/battle_options.py` 23, `battle/aiming_angles.py` 13,
`views/hangar/hangar_options_hooks.py` 12 e `battle/dispersion_circle.py` 11.
Estes valores servem para priorizar revisão, não para declarar todos esses hooks
desnecessários.

### Como o Battle Observer os organiza

- Um helper guarda o método anterior, identifica a instalação por
  classe/método/handler e evita repetir a mesma instalação registada.
- `toggleOverride` permite ligar/desligar hooks segundo as configurações.
  Há exemplos concretos na dispersão e na filtragem do canal de serviço.
- Vários módulos subscrevem serviços/eventos, com remoção em `fini` ou no ciclo
  de vida da vista. O teclado usa `InputHandler` e eventos de contexto partilhados.
- Os hooks concentram-se nas alterações de comportamento ou apresentação que
  os eventos disponíveis não exprimem diretamente.

Não copiar cegamente o cancelamento: repor o método guardado com `setattr` pode
apagar um hook instalado depois por outro mod. O helper dele também tenta
resolver nomes por semelhança; preferir contratos explícitos e verificados para
a versão do jogo. A referência é útil, mas não elimina estes riscos técnicos.

### Estado do nosso gestor de hooks

`core/hooks.py` já associa hooks a um proprietário e impede a execução do handler
quando o proprietário está inativo. Porém, `deactivate()` deixa os wrappers na
cadeia e só desativa o comportamento. Isto preserva a cadeia, mas não elimina o
custo dos encaminhamentos. Não há ali um registo explícito por alvo/handler com
token de instalação e remoção; avaliar idempotência nesse nível.

Também existem instalações diretas através de `common/utils/monkeypatch.py`,
incluindo a ponte de eventos antiga e serviços centrais. A consolidação deve
ter um único proprietário por alvo partilhado.

### Ordem de redução recomendada

1. Consolidar startGUI/destroyGUI. Cada módulo torna-se consumidor dos eventos
   centrais; retirar o produtor antigo de `common/utils/events/player_avatar.py`.
   Preservar a ordem before/after: há limpezas que precisam de ocorrer antes
   do destroy original. Um evento genérico sem essa distinção não é equivalente.
2. Consolidar saúde, aparência e feedback de batalha. Preservar os argumentos
   necessários: o evento atual de saúde publica apenas veículo/HP, enquanto
   consumidores existentes precisam também de HP anterior, atacante ou motivo.
3. Avaliar os dois hooks de handleKey com o KeyboardService já existente.
   Observar uma tecla não garante que o comando tenha sido aceite pelo jogo.
   Preservar as condições de recarga, movimento e contexto antes de migrar.
4. Rever os hooks de hangar. Existem caminhos Scaleform antigos e caminhos
   Gameface atuais para opções relacionadas; verificar a utilização no cliente
   alvo antes de retirar os antigos. Limitar `ViewImpl.createToolTip` às classes
   específicas onde for possível, reduzindo o âmbito global.
5. Rever os caminhos frequentes da mira/câmara: evitar consultas repetidas das
   mesmas configurações e partilhar dados. Manter hooks que realmente alteram
   argumentos, retornos ou comportamento nativo sem alternativa equivalente.
6. Unificar o registo por alvo/proprietário e controlar duplicações. Instalar
   apenas quando necessário e limpar com verificação de propriedade da cadeia.

Uma primeira redução plausível é passar os 17 pontos de start/destroy para dois
produtores centrais, retirando até 15 instalações declaradas nesses alvos.
Isto é uma hipótese de refatoração a validar, não uma redução já implementada.
Não há objetivo de igualar a contagem do Battle Observer: cada hook restante
deve ter motivo, proprietário, contexto, contrato de argumentos/retorno e limpeza.

### Critérios de verificação

- Método original chamado exatamente o número de vezes previsto, mantendo
  argumentos, retorno e exceções; exceções de um consumidor não podem impedir
  outros consumidores nem a operação nativa quando esta deve ocorrer.
- Entrada/saída repetidas em batalha, replay e hangar sem listeners duplicados.
- Desativação e reativação sem acumular wrappers ou interferir com outros mods.
- Diagnóstico local por alvo: proprietário, motivo, estado, número de handlers;
  medir frequência/tempo nos caminhos críticos antes de afirmar ganhos.
- Regressão de recarga com C, Safe Shot, estatísticas, mira/câmara, painéis e
  limpeza de recursos. Testes continuam locais, conforme pedido do utilizador.

Executar esta consolidação como parte da refatoração do arranque e das
configurações, antes de publicar uma atualização do modpack.
