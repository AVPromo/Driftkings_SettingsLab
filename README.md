# Driftkings

Modpack for Wargaming World of Tanks: battle overlays, hangar improvements and an integrated settings panel.

## Downloads

**[Download the beta](https://github.com/dkruben/Driftkings_SettingsLab/releases/tag/v0.1.2-beta.3)** · [All releases](https://github.com/dkruben/Driftkings_SettingsLab/releases)

Current version: **0.1.2-beta.3**, for **WoT 2.4.1.0**. Beta releases remain under refinement.

## Battle interface and statistics

- Player panels and battle-loading statistics.
- Gameface gun-mark panels in battle and hangar, battle statistics and High Caliber progress.
- Own-vehicle health, target information and distance markers.
- Minimap options, spotted indicators and Sixth Sense customization.

## Camera and aiming

- Zoom and aiming-angle options.
- Dispersion circle, aiming timer and shell flight time.
- Armor calculator, artillery splash and server-turret display.
- Native autoaim target highlighting.

## Hangar and utilities

- Carousel statistics and gun-mark information.
- Hangar presentation and crew options.
- Clan reward collection and battle-efficiency information.
- Integrated settings, profiles and beta/stable update channels.

Available behavior depends on configuration, vehicle and game mode.

## Installation

1. Close World of Tanks.
2. Download `Driftkings-0.1.2-beta.3-WoT-2.4.1.0.zip` from the release assets.
3. Extract its `mods` folder into the game installation, merging folders. It includes Driftkings and the required ModsListAPI and OpenWG Gameface packages under `mods/2.4.1.0/`.
4. For a new installation, extract the separate `Driftkings-defaults.zip` into the game installation. Preserve existing `mods/configs/Driftkings` settings when updating.
5. Start the game and open Driftkings settings through the mods list.

The defaults are the author's selected mod configurations. Existing personal JSON files take precedence. The in-game updater preserves those configurations; missing settings use packaged defaults.

## Compatibility and beta status

Designed for Wargaming EU, NA and ASIA clients; Mir Tankov/RU is outside scope. This beta was checked locally on EU 2.4.1.0, including normal startup and a battle replay. Other realms and every feature have not been fully validated in-game. MarksOnGun panel dragging was confirmed on NA in the hangar and battle replay; complete mark estimates still need live-battle validation. A complete update through the in-game updater remains to be validated.

## Languages

Settings translations: Czech, German, English, Spanish, French, Hungarian, Italian, Japanese, Korean, Polish, Portuguese, Russian, Thai, Turkish, Ukrainian, Vietnamese, Simplified Chinese and Traditional Chinese. Translation corrections are welcome.

## Build from source

This repository contains the compiler, runtime sources, defaults and required resource inputs. Generated packages, Python bytecode, caches and local tests are excluded from Git. Download compiled packages from Releases.

On Windows, configure Python 3.10+, Python 2.7, Java/Flex, playerglobal and game SWCs, the .NET C# compiler. Game and reference directories are external read-only inputs.

```powershell
python build_tools/compiler.py --plan
python build_tools/validate_build_data.py
.\debug.cmd
.\release.cmd --version 0.1.2-beta.3 --channel beta
```

Check portable logic with `python -m unittest discover -s tests/settings_panel -p 'test_*.py'` and `python -m unittest discover -s tests/core -p 'test_*.py'`; both suites also run on Python 2.7. Run `node tests/settings_panel/test_gameface.js` for the Gameface state tests. Install development dependencies with `npm ci --ignore-scripts`, then run `npm run lint` to enforce ES5 syntax and basic JavaScript checks. These tools run on Node 20.19+; client scripts remain ES5.

Edit defaults in `res/configs/Driftkings/default/`, then run `python build_tools/generate_defaults.py --write` to regenerate the Python fallback. For intentional changes to the default values, also refresh the recorded snapshot with `python build_tools/generate_defaults.py --write --refresh-snapshot`. Use `python build_tools/generate_defaults.py --check` to check synchronization without writing files; never edit `settings/default_values.py` by hand.

The current build contract uses the (EU, NA) installation as its resource source and an EU source reference. Local tool paths belong in ignored `build_data/toolchain.local.json`. Builds compile Python 2.7 to standard bytecode without obfuscation, Flash and native helpers, generate the carousel integration and verify the packages. Outputs go to `build/`; compilation does not install or publish them.

| Directory | Contents |
| --- | --- |
| `mod/res` | Runtime Python, Gameface and packaged resource inputs |
| `flash_source` | ActionScript sources and compilation libraries |
| `installer/source` | Native helper sources |
| `build_data` | Build contracts, components, targets and release metadata |
| `build_tools` | Compiler, validators and release tooling |
| `res` | Canonical defaults, dependencies and resource sources |

The next beta introduces descriptive module and configuration names, with migration for existing profiles.

## Image paths in the next beta

Overlay images and custom Sixth Sense icons accept `gui/maps/Driftkings/...` resources or user files in `mods/configs/Driftkings/...`, including their fixed SWF-relative forms. `img://` prefixes remain supported. Move custom images from other folders into `mods/configs/Driftkings/` and update their configuration paths. External URLs, absolute paths and directory traversal are rejected; overlays use their configured alternative image, and Sixth Sense uses its embedded fallback icon when loading fails.

## Support and credits

[Report an issue](https://github.com/dkruben/Driftkings_SettingsLab/issues) with the mod version, game version/realm, reproduction steps and relevant `game.log` excerpts. Remove personal information before sharing logs.

Dependencies: ModsListAPI by poliroid and OpenWG Gameface.
