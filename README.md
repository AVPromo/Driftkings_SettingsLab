# Driftkings SettingsLab

Python client modules, battle overlays, hangar interfaces and an owned settings manager for Wargaming World of Tanks. Distribution uses `.wotmod` for EU/NA/ASIA; Mir Tankov/RU and `.mtmod` are outside scope. Target scope is not Wargaming certification or proof of testing on every realm.

## Target and status

Source version: `0.1.2-beta.1`, from [runtime version](mod/res/scripts/client/Driftkings/__init__.py). [Build config](build_data/build_config.json) targets client `2.4.1.0` / EU dump `2.4.1.5488`. Native WG resources, updated Carousel integration and SWCs are included in the diagnostic build. **Real client and regional validation remain pending.** See the [2.4.1 migration report](docs/migration/2.4.1/FINAL_REPORT.md).

The historical 2.4.0.2 diagnostic package passed automated checks and client startup on 2026-10-14. **Full client functional validation remains pending.** It contained **33 components / 255 pycs / 421 entries**. Current local modifications are not certified by that historical package. See the [handover](docs/architecture/DRIFTKINGS_ARCHITECTURE_HANDOVER.md) for evidence, hashes and limits.

AutoAimOptimize displays a box around the native autoaim target. Assisted acquisition, vehicle scanning and custom locking were removed; preserve this policy.

## Repository

| Path | Role |
| --- | --- |
| [mod/res/scripts/client](mod/res/scripts/client) | Runtime Python; entrypoint `gui/mods/mod_Driftkings.py` |
| [mod/res/gui](mod/res/gui) | Canonical Flash, Gameface and map assets |
| [build_data](build_data) | Targets, component definitions, locales and package contracts |
| [build_tools](build_tools) | Existing build, package, audit and test tools |
| [build_tools/tests](build_tools/tests) | Regression tests; fixtures retain their current paths |
| [flash_source](flash_source/README.md) | One active battle project, shared AS3 and external SWCs |
| [installer/source](installer/source) | Native updater and WindowsFiles C# helper sources |
| [res](res) | Config presets, external inputs, Wwise sources and historical resources |
| [docs](docs/README.md) | Guides, contracts, history and maintenance plans |
| `build/` | Current outputs, including `build/native/`; `installer/build/` retains historical evidence |

## Development and commands

Development uses Python 3 and PowerShell on Windows; client sources retain Python 2.7 compatibility. Compilation uses SourceTree's embedded Python 2.7 host; focused probes also reference standalone Python 2.7. Flash requires Java, Flex, playerglobal and game SWCs. Native helpers require the Windows .NET compiler; protected builds additionally require PJOrion. Game/reference resources are external, read-only inputs.

Run from the repository root after reviewing the [build guide](UNIFIED_BUILD.md):

```powershell
python -m unittest discover -s build_tools/tests
python build_tools/localize_configs.py --check
python build_tools/check_flash_contracts.py
python build_tools/build_lab.py --flash --no-obfuscation
```

`debug.cmd` and `release.cmd` invoke the existing PowerShell chain. `build_lab.py --flash` now compiles into `build/flash` and packages that output without overwriting the tracked SWF. Direct `build_flash.py --publish` still overwrites it. Release mode additionally runs selective protected-beta tooling. Neither wrapper deploys to the game or publishes to GitHub. Native installation tests require WoT closed. No build or runtime test was executed for CLEANUP-B1.

Overrides: `DK_PYTHON3` for wrappers; `--hg` for the embedded compiler host; `DK_FLEX_HOME`, `DK_MXMLC_JAR`, `DK_PLAYERGLOBAL`, `DK_JAVA` for Flash. See [reference updates](TOOL_UPDATES.md). Fixed local paths and CI provisioning gaps remain. CI configures Ubuntu/Python 3.12, Python 2.7 syntax parsing and selected JavaScript tests; it does not provision the complete Windows/native/Flash toolchain or prove a successful latest remote run.

## Package and settings

The unified package is `build/unified/Driftkings.wotmod`. Builders also produce `PlayerPanelPro-XVM-preset.zip`, `PlayerPanelPro-HP-Spotted-preset.zip` and `Driftkings-Carousel.zip`. Protected beta metadata is separate. The Carousel ZIP validates its nine canonical icon inputs and preserves a previous ZIP on failure; see [repository maintenance](docs/development/REPOSITORY_MAINTENANCE.md).

Selected 2.4.1 UI dependencies are ModsListAPI 1.8.0 and OpenWG Gameface 1.2.2 in `build/dependencies/2.4.1/`; the build rejects missing or extra packages there. Old `res/wotmods/` packages are historical inputs. Dependency preparation and evidence: [migration discovery](docs/migration/2.4.1/DISCOVERY.md). Deployment requires separate authorization and preservation of existing `mods/configs/Driftkings/` settings.

Defaults live in [settings/settings_data.py](mod/res/scripts/client/Driftkings/settings/settings_data.py); menus live in [settings/templates/](mod/res/scripts/client/Driftkings/settings/templates). Profiles, formats, persistence and i18n remain supported. See [configuration](docs/CONFIGURATION.md) and [metadata](docs/SETTINGS_METADATA.md).

## Architecture, UI and updater

The four canonical config classes belong to `Driftkings.settings.config_interfaces`; legacy facades preserve same-object compatibility. Presenter, EditSession, Registry, SettingsService and TemplateAdapter retain their existing owners.

Settings/hangar use Gameface. Battle retains the owned Scaleform/DAAPI library and Python/AS3 contracts. OpenWG owns global injection/resource registration; Driftkings owns feature lifecycle. See [UI bridge](docs/UI_BRIDGE.md) and [4B.8 closure](docs/architecture/PHASE4B8_FINAL_ARCHITECTURE.md).

The updater and [native helper](docs/UPDATER_INSTALLER.md) retain verification, installation/rollback and restart contracts. WindowsFiles pre-validation hardening remains **OPEN HIGH**, separate work before stable. PJOrion keeps exactly three allowlisted bytecodes; a diagnostic build does not certify a protected release.

BanksLoader now consolidates audio XML directly into the client version's loose overrides. It does not require `_aaa_BanksLoader_audioMods.wotmod` or create new `_BanksLoaded.wotmod` archives. See [audio configuration](docs/BANKS_LOADER.md); real client sound validation remains pending.

## Licensing and support

Read [English license](LICENSE_EN.md), [Portuguese license](LICENSE_PT.md), [XVM license](docs/XVM-CONFIG-LICENSE.txt) and [XVM notice](docs/XVM-CONFIG-NOTICE.md). Third-party SDK, SWC, sound and API redistribution rights require provenance review; repository presence does not establish permission.

Report issues in [dkruben/Driftkings_SettingsLab](https://github.com/dkruben/Driftkings_SettingsLab/issues) with client/mod version, reproduction steps and relevant `game.log` excerpts. Start with the [documentation index](docs/README.md). Historical phase evidence retains its original paths.
