# Driftkings configuration installer

Build inputs, scripts and previews for an **Inno Setup 6.7.1+** installer. Images can be supplied later; see [assets/README.md](assets/README.md). All outputs stay in ignored `build/` directories. Building never installs, starts the game, publishes a release or changes user settings.

```powershell
# Generate/validate choices without game artifacts or Inno (also runs in CI):
python build_tools/build_installer.py

# Build the regular modpack first, then compile the installer:
python build_tools/compiler.py --mode debug --version 0.1.2-beta.4
python build_tools/build_installer.py --artifacts build/debug/beta/0.1.2-beta.4 --compile
```

`--iscc` overrides the compiler path. Generated includes go to `build/installer_input/`; the EXE goes to `build/installer/`. The installer is target-specific: it checks the selected game's `version.xml` against the build version/realm and blocks installation while WorldOfTanks.exe is running. It does not close or restart the game.

## Contract and choices

- The current catalog contains **28** top-level JSON components with `enabled`, **one** extra option and **zero** additional presets. Counts are derived, not a second maintained component list. `sound_bank_loader` has no `enabled` and is excluded. Multi-document sections such as `team_panels` and `vehicle_carousel` keep their packaged defaults.
- `generate_ui_catalog.installer_catalog()` reads default JSON and manifest entrypoints. Labels/descriptions and category names come from the English/Portuguese catalogs. Missing labels fail the build. If there is no separate tooltip description, the existing descriptive title is used.
- `components.generated.iss` contains the component page and Pascal name/file/key mapping. Handwritten scripts never maintain these names. The recommended type uses the author's packaged defaults; custom selection changes booleans only.
- `presets.json` accepts `{"presets":[{"key":"owner_choice","labels":{"en":"Owner choice","pt":"Escolha do autor"},"disabled":["clan_reward_collection"]}]}`. Keys must identify existing selectable components. No minimum preset is supplied.
- `options.json` contains top-level boolean settings and i18n label keys. Initially, only `sixth_sense_alert.userSound` is exposed as a task. That option controls playback of the configured Wwise event (subject to the existing `playTickSound` logic); it does not install or remove banks.
- `payload.generated.iss` always installs the same unified WOTMOD and the two dependencies from a verified compiler output. No `Components:` or `Tasks:` condition can change that payload. Banks/icons stay inside the existing WOTMOD inventory. Previews are temporary wizard-only resources.

Existing shared dependencies must already match the verified payload; different bytes at the same filename stop installation before copying. Matching dependencies are kept and never uninstalled. All three installed WOTMOD hashes are checked before any configuration is written.

## Why minimal JSON files

The active configuration path is `settings/loader.py`, rather than the legacy `common/config/json_reader.py` facade. `validate_types()` accepts missing keys and `SettingsLoader.load()` merges a partial object with packaged defaults through `settings/store.merge()`. The installer therefore writes only fields that differ from defaults, e.g. `default/clan_reward_collection.json` containing `{"enabled":false}`, plus `load.json` pointing to `default`. An all-default installation needs no component JSON files. The real loader is covered by an installer test that checks merging and preservation of the partial file's bytes.

`SOURCE_HASHES` is generated audit metadata; no runtime module reads it to trigger migration or warnings. Installer-written partial files do not affect the defaults snapshot or generated source. Existing component-specific normalization/migration remains unchanged.

## Reinstall, reset and uninstall

An existing profile/selector/legacy configuration skips both choice pages. The installer does not rewrite any existing JSON. User media READMEs are created only if absent.

`/RESETCONFIG=1` explicitly opts into a reset (interactive or silent). First, all configuration JSON and known `.json.previous`/`.json.bak` recovery files are copied, preserving relative paths, into `mods/configs/Driftkings/installer-backup/<timestamp>-<suffix>/`. Only after the entire backup succeeds are originals removed and the selected partial defaults written. This resets all profiles and JSON translation overrides, then selects `default`. Media directories, cache, installer files and previous installer backups are excluded. Reparse points in configuration paths block reset. On a detected write failure, created JSON files are removed and the original backup is restored where possible; backups remain available. Power loss/crashes during installation still require manual recovery from that backup.

Example silent invocation: `Driftkings-...-Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="D:\Games\World_of_Tanks_NA" /RESETCONFIG=1 /TYPE=recommended`. Component names include their generated group prefix; use `choices.generated.json` and the generated `.iss`, rather than guessing a manual list. Inno's `/TASKS` controls extra options.

The uninstaller never removes the custom-media directories, configuration JSON, their backups or shared dependency WOTMODs. It removes its own code WOTMOD and installer files. No recursive cleanup of the configuration tree is performed.

In-game **reset to defaults** still restores the defaults packaged by the author, **not** the user's installer choices. A possible future improvement is an `installer_choices.json` baseline understood by the settings system; that is deliberately not implemented here.

## Manual Windows checks still required

- Install recommended/all components into a matching client; open the settings panel and check their defaults.
- Deselect `clan_reward_collection` and `game_log_manager`; confirm only those are disabled and all other values retain packaged defaults.
- Toggle the Sixth Sense sound task and confirm its runtime meaning independently of whether the component itself is enabled.
- Reinstall over personalized settings, including a non-default profile and recovery selector; compare JSON bytes before/after.
- Run `/RESETCONFIG=1` interactively and silently; confirm complete backups and the new default profile. Check recovery after a simulated write failure on a disposable test installation.
- Uninstall with user files inside both custom-media directories; confirm those files/configs/backups and shared dependencies survive.
- Supply/replace branding images and a component PNG preview, rebuild, then check rendering/selection at different DPI settings. Missing images should use defaults/no preview.
- Add a new packaged `.bnk`/matching XML pair, declare both in `components.json`, rebuild and confirm the sound bank loader discovers/loads it in the game. Sound packs cannot become optional payloads without extending the updater inventory/helper first.

Pure generator/media tests run in CI. The Windows EXE is compiled locally; these tests do not simulate installation or the game's sound engine.

## WG client discovery

See [the Portuguese installer guide](GUIA_INSTALADOR_PT.md) for discovery scope, supported versions/realms, side-by-side uninstall registration and exact branding/preview paths. Clients outside the bounded registry/common-folder search can be selected manually.
