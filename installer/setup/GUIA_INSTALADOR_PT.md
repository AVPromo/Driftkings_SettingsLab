# Guia do instalador Driftkings

## Onde colocar as imagens

As pastas já existem. Todos os caminhos seguintes são relativos à raiz deste repositório.

| Uso | Ficheiro | Formato e tamanho recomendado |
| --- | --- | --- |
| Ícone do executável | `installer/setup/assets/branding/setup-icon.ico` | ICO com 16, 32, 48, 64 e 256 px |
| Imagem de boas-vindas e conclusão | `installer/setup/assets/branding/wizard-large.png` | PNG, 430 × 824 px, proporção 164:314 |
| Imagem pequena do cabeçalho | `installer/setup/assets/branding/wizard-small.png` | PNG quadrado, 147 × 147 px |
| Pré-visualização de cada mod | `installer/setup/assets/previews/<nome_do_componente>.png` | PNG, por exemplo 600 × 360 px; ajustado proporcionalmente |

Também podes usar `wizard-large.bmp` e `wizard-small.bmp`. Se houver BMP e PNG com o mesmo nome, o BMP tem prioridade. O ícone tem de ser ICO verdadeiro: mudar a extensão de um PNG não o converte.

As imagens são opcionais. Sem branding usam-se os recursos do Inno; sem preview não se mostra imagem. As imagens do instalador não são copiadas para o jogo. Não colocar aqui os ícones personalizados dos jogadores: esses ficam em `mods/configs/Driftkings/SixthSense/` ou `mods/configs/Driftkings/images/`, dentro de cada cliente.

Exemplo: para uma imagem do Sexto Sentido, colocar `installer/setup/assets/previews/sixth_sense_alert.png`.

### Nomes atuais disponíveis para previews

- `aiming_countdown.png`
- `aiming_reticles.png`
- `artillery_blast_radius.png`
- `autoaim_target_indicator.png`
- `battle_marks_of_excellence.png`
- `battle_performance.png`
- `battle_preferences.png`
- `battle_statistics.png`
- `clan_reward_collection.png`
- `crew_management.png`
- `enemy_spotting_status.png`
- `game_log_manager.png`
- `gun_traverse_limits.png`
- `hangar_marks_of_excellence.png`
- `hangar_preferences.png`
- `high_caliber_progress.png`
- `minimap_enhancements.png`
- `penetration_indicator.png`
- `repair_controls.png`
- `server_turret_sync.png`
- `shell_flight_time.png`
- `sixth_sense_alert.png`
- `sniper_camera.png`
- `target_distance.png`
- `target_information.png`
- `tech_tree_marks_of_excellence.png`
- `third_person_zoom.png`
- `vehicle_health.png`

Esta lista corresponde aos componentes atuais; a fonte é o catálogo gerado, não uma lista manual no script Inno. Depois de gerar, consultar `build/installer_input/choices.generated.json` se forem adicionados módulos.

## Compilar

Executar na raiz do projeto, com Python 3, Python 2.7, Flex e Inno Setup 6.7.1 ou superior disponíveis nas localizações configuradas/detetadas:

```powershell
python -B build_tools/validate_build_data.py
python -B build_tools/compiler.py --mode debug --version 0.1.2-beta.4
python -B build_tools/build_installer.py --artifacts build/debug/beta/0.1.2-beta.4 --compile
```

O EXE é escrito em `build/installer/`. Estes comandos compilam; não instalam nem publicam. Usar a versão pretendida nos dois últimos comandos. Para uma distribuição final, usar o modo `release` do compilador e a pasta correspondente. Depois de trocar apenas imagens, basta repetir o comando do instalador com os mesmos artefactos; se alterares código/defaults, recompilar primeiro o modpack.

O processo segue a organização do instalador antigo: script principal, lógica do assistente separada, branding separado e previews por componente. Não depende de DLLs ou imagens da pasta antiga `wot.driftkings`.

## Deteção de clientes WG

O assistente procura instalações nas entradas de desinstalação do Windows, em HKCU e HKLM, nas vistas de 32 e 64 bits. Procura também nas pastas imediatas habituais das unidades locais fixas: raiz, `Games`, `Wargaming.net`, `Games/Wargaming.net` e Program Files. Não faz uma pesquisa recursiva de todo o disco. Instalações portáteis em caminhos diferentes podem ser selecionadas manualmente.

A lista mostra região, versão e caminho. A região vem de `version.xml`, não do nome da pasta ou da chave do registo; SEA é normalizado para ASIA. A raiz tem de conter `version.xml`, `res/packages` e o executável na raiz, em `win64` ou em `win32`. Selecionar uma subpasta do jogo também permite resolver a raiz.

A pasta é validada ao sair da página e novamente antes de copiar. A instalação é recusada se a versão/região não corresponder aos artefactos. A versão atualmente compilada é 2.4.1.0, com EU, NA e ASIA configurados em `build_data/build_config.json`, campo `game.supported_realms`. Uma nova versão do jogo exige recompilação e validação das alterações Gameface; não basta mudar o destino para uma pasta de versão nova.

Cada raiz recebe uma identidade de desinstalação própria, para permitir instalações EU e NA lado a lado. Instalar uma instância de cada vez, escolhendo-a na lista. Uma execução não instala automaticamente em todos os clientes. A opção `/DIR="D:\Games\World_of_Tanks_NA"` fixa o destino em utilização silenciosa; um destino explícito inválido é recusado em vez de ser substituído por outro cliente.

As escolhas só alteram configurações JSON. O código e dependências instalados são os mesmos para todas as escolhas. As configurações existentes são preservadas; `/RESETCONFIG=1` é uma reposição explícita com backup. Ver `README.md` desta pasta para os detalhes de reposição e recuperação.

## Validação e limites

Compilação completa do modpack e do EXE verificada localmente. Os três recursos Gameface usados nas patches têm os hashes esperados nos clientes EU e NA locais. Não há um cliente ASIA local para confirmar essa parte. Os testes de contrato não executam a interface Inno nem simulam uma instalação real.

Antes de distribuir, confirmar no Windows: lista e seleção EU/NA/ASIA; caminho personalizado; recusa de outra versão; instalação e desinstalação em duas instâncias; preservação de JSON; branding/previews e escalas DPI. Não foi efetuada instalação automática nos teus clientes.

Referências oficiais: [AppId por instalação](https://jrsoftware.org/ishelp/topic_setup_appid.htm), [imagem principal](https://jrsoftware.org/ishelp/topic_setup_wizardimagefile.htm), [ícone](https://jrsoftware.org/ishelp/topic_setup_setupiconfile.htm).
