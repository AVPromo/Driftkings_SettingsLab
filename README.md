# Driftkings SettingsLab

Current priorities and next steps: [Plano de trabalho](PLANO_TRABALHO.md).

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
| [build_data](build_data/README.md) | Schema 1: targets, component definitions, defaults and package contracts |
| [build_tools](build_tools/README.md) | Compiler, build-data validator and explicit release publication |
| [flash_source](flash_source/README.md) | One active battle project, shared AS3 and external SWCs |
| [installer/source](installer/source) | Native updater and WindowsFiles C# helper sources |
| [res](res) | Config presets, external inputs, Wwise sources and historical resources |
| [docs](docs/README.md) | Guides, contracts, history and maintenance plans |
| `build/` | Current outputs, including `build/native/`; `installer/build/` retains historical evidence |

## Development and commands

Development uses Python 3 and PowerShell on Windows; client sources retain Python 2.7 compatibility. Compilation uses SourceTree's embedded Python 2.7 host; focused probes also reference standalone Python 2.7. Flash requires Java, Flex, playerglobal and game SWCs. Native helpers require the Windows .NET compiler; protected builds additionally require PJOrion. Game/reference resources are external, read-only inputs.

Read the [compiler guide](build_tools/README.md) and [build-data contract](build_data/README.md). From the repository root:

```powershell
python build_tools/validate_build_data.py
python build_tools/validate_build_data.py --check-game --write-plan build/build_plan.json
.\debug.cmd
.\release.cmd
```

`debug.cmd` builds a diagnostic package; `release.cmd` applies the configured protection policy. Both compile Python 2.7, Flash and native helpers, generate resources, and verify the completed package. Neither installs into the game nor publishes to GitHub. Release outputs are separated by channel and mod version under `build/releases/`; debug outputs use `build/debug/`. Failed compilation preserves earlier completed outputs.

The data contract selects the NA installation as the read-only game resource source and the EU dump as the read-only Python/AS3 reference. CI validates build data, configuration JSON, Python 2.7 syntax and JavaScript syntax. It does not provision a complete compiler toolchain or prove in-game behavior.

## Package and settings

The latest validated unified output is `build/unified/Driftkings.wotmod`. The compiler generates the battle SWF, native helpers and patched carousel Gameface bundle before packaging. All ten carousel PNGs belong inside the WOTMOD; runtime icon loading uses mounted resources through `ResMgr`. Versioned builds also contain `release.json`, a distribution ZIP, separate defaults, dependencies and checksums.

Selected 2.4.1 UI dependencies are ModsListAPI 1.8.0 and OpenWG Gameface 1.2.2 in `res/wotmods/`, pinned by SHA-256 in `build_data/build_config.json`. Defaults in `res/configs/Driftkings` now come from the NA installation's default profile and are installed separately from the WOTMOD, preserving existing user settings. Deployment requires separate authorization.

Distribution defaults live in [res/configs/Driftkings](res/configs/Driftkings). Python fallbacks in `settings/default_values.py` are generated from those JSON files; `settings/settings_data.py` retains settings metadata and accessors. Regenerate after intentional edits with `python build_tools/generate_defaults.py --write --refresh-snapshot`. The compiler regenerates the packaged fallback directly from JSON. Section declarations live in [settings/definitions/](mod/res/scripts/client/Driftkings/settings/definitions). Profiles, formats, persistence and i18n remain supported.

## Architecture, UI and updater

`settings.service.SettingsService` owns section initialization, JSON persistence and change notifications. `settings/definitions` declares controls and feature normalization; `controls_schema.py` resolves declarative metadata, and `panel/sections.py` binds it to the owned Gameface panel. ConfigInterface, ConfigNoInterface, TemplateBuilder and the old template adapter have been removed. Existing JSON formats and persisted panel identities remain compatible. Core startup now uses lazy service factories with explicit dependencies and partial-failure cleanup. Shared battle/login/hangar events replace duplicate observer hooks; subscriptions follow their component owner. `interface_catalog.py` now declares Flash/Gameface contracts and ordered resources, with generated AS3/JS catalogs verified by the build. The single battle SWF has separate battle and ratings factories. The next phase covers compatibility and game modes; in-game validation is deferred until the end of the reorganization.

Settings/hangar use Gameface. Battle retains the owned Scaleform/DAAPI library and Python/AS3 contracts. OpenWG owns global injection/resource registration; Driftkings owns feature lifecycle. Current interface contracts and validation limits are recorded in the [reorganization plan](PLANO_TRABALHO.md).

The updater and [native helper](docs/UPDATER_INSTALLER.md) retain verification, installation/rollback and restart contracts. WindowsFiles pre-validation hardening remains **OPEN HIGH**, separate work before stable. PJOrion keeps exactly three allowlisted bytecodes; a diagnostic build does not certify a protected release.

BanksLoader now consolidates audio XML directly into the client version's loose overrides. It does not require `_aaa_BanksLoader_audioMods.wotmod` or create new `_BanksLoaded.wotmod` archives. See [audio configuration](docs/BANKS_LOADER.md); real client sound validation remains pending.

## Licensing and support

Read [English license](LICENSE_EN.md), [Portuguese license](LICENSE_PT.md), [XVM license](docs/XVM-CONFIG-LICENSE.txt) and [XVM notice](docs/XVM-CONFIG-NOTICE.md). Third-party SDK, SWC, sound and API redistribution rights require provenance review; repository presence does not establish permission.

Report issues in [dkruben/Driftkings_SettingsLab](https://github.com/dkruben/Driftkings_SettingsLab/issues) with client/mod version, reproduction steps and relevant `game.log` excerpts. Start with the [documentation index](docs/README.md). Historical phase evidence retains its original paths.
