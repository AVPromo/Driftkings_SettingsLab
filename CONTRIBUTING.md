# Contributing to Driftkings

This guide explains how the code is organised and how to make a change safely. For building and installing, see the [README](README.md).

## Ground rules

- **Client scripts run on Python 2.7** (the World of Tanks client). Write code that is valid on both 2.7 and 3: no f-strings, no type hints, no `nonlocal`, no keyword-only arguments. CI parses every client source with Python 2.7.
- **Gameface JavaScript is ES5.** `npm run lint` enforces this.
- **Use `logging`, never `print`.** Each module declares `LOG = logging.getLogger('Driftkings.<Area>')`. Use `LOG.exception(...)` inside `except` blocks so the traceback reaches the game log.
- **Do not swallow exceptions silently.** Catch the narrowest exception type, and either log it or explain in a comment why ignoring it is correct.
- Prefer **pure, engine-free modules** for logic (see `core/gun_stats.py`, `core/carousel*.py`, `core/high_caliber.py`). They can be tested without the game.
- Never edit generated files by hand: `settings/default_values.py` and `component_list.py` are generated.

## Repository layout

| Path | Contents |
| --- | --- |
| `mod/res/scripts/client/Driftkings` | Runtime Python (the mod itself) |
| `mod/res/gui/gameface` | Gameface HTML, CSS and ES5 JavaScript |
| `res/configs/Driftkings/default` | Canonical default settings (JSON) |
| `flash_source` | ActionScript sources for the battle SWFs |
| `installer` | Windows installer script and the native C# helper |
| `build_data`, `build_tools` | Build contracts, validators, compiler and release tooling |
| `tests` | Portable tests (`core`, `settings_panel`, `installer`) |

Inside the client package:

- `core/` – composition, lifecycle, hooks, keyboard, callbacks, updater, and pure logic helpers.
- `settings/` – settings service, profiles, store, panel (presenter, controls, sections) and `definitions/`.
- `battle/`, `lobby/`, `components/` – the feature components.
- `views/` – Scaleform/Gameface presentation for those components.
- `common/` – shared utilities (colours, config reading, monkeypatching helpers).
- `i18n/` – one translation catalogue per language.

## Architecture

### Core and services

`core/__init__.py` composes the mod explicitly:

1. **Services** are declared as `ServiceSpec(name, factory, requires, phase)`. A service starts only when all the services it `requires` are `active`; otherwise it is marked `blocked`. Factories hold import *paths*, so no engine module is touched until the service really starts. Services are stopped in reverse order.
2. **Components** are the modules listed in `component_list.py` (for example `battle.target_information`). Core imports each one, which *declares* its hooks, then starts the `interface` services, then calls the module's `init()`. A component can declare `REQUIRES_SERVICES`, and optionally `getBattleViews()` / `getWindowViews()`. `fini()` is called on shutdown.
3. A component that fails to import or initialise is **disabled and logged** (`LOG.exception`), and its settings are disabled; it must never take the rest of the mod down.

### Hooks

Patching game code goes through `core/hooks.py`, never directly through ad-hoc monkeypatching:

```python
from Driftkings.core.hooks import override, overrideMethod, on_event

@overrideMethod(PlayerAvatar, 'onEnterWorld')
def onEnterWorld(original, avatar, *args, **kwargs):
    result = original(avatar, *args, **kwargs)
    ...
    return result
```

Hooks are declared at import time and **owned by their component**. They are only installed while the owner is active; when it is inactive the wrapper simply delegates to the original function. Always call `original`, and keep handlers small and defensive.

### Settings

- Defaults live as JSON under `res/configs/Driftkings/default/`. After editing them run `python build_tools/generate_defaults.py --write` (and `--refresh-snapshot` for intentional default changes). CI runs `--check`.
- A component's settings class lives in `settings/definitions/<area>/<name>.py` and extends `SectionDefinition`. Read values through `settings_service.getComponentDict(config)` and react to changes with `affects(changes, ...)`.
- Names and menu text are translated through the `i18n` catalogues. Add new keys to **every** language (English text is an acceptable placeholder) and run `python build_tools/validate_locales.py`.

## Adding a component

1. Create the module under `battle/`, `lobby/` or `components/` with `init()` (and `fini()` if it holds state).
2. Declare its hooks with the decorators above; keep calculations in a pure module under `core/` when possible.
3. Add its defaults JSON, settings definition, constants and translations.
4. Register it in the component catalogue and the build data (`build_data/components.json`), then run `python build_tools/validate_build_data.py`.
5. Add tests for any pure logic.

## Testing

Run these before opening a pull request (they are the same checks as CI):

```bash
python -m unittest discover -s tests/core -p 'test_*.py'
python -m unittest discover -s tests/settings_panel -p 'test_*.py'
python -m unittest discover -s tests/installer -p 'test_*.py'
python build_tools/validate_build_data.py
python build_tools/validate_locales.py
python build_tools/generate_defaults.py --check
npm ci --ignore-scripts && npm run lint && node tests/settings_panel/test_gameface.js
```

`tests/core` and `tests/settings_panel` also run on Python 2.7 in CI; if you have Docker you can reproduce that with the `python:2.7` image. Tests load real production modules through `tests/core/support.py` with the engine stubbed at the import boundary, so avoid importing `BigWorld`, `gui.*` or `Avatar` from code you want to test.

Behaviour inside the game still needs manual verification against the target client. Say in the pull request which client version and mode you tested.

## Signing releases

The updater can authenticate `release.json` with an Ed25519 signature (free, no certificate authority). It is **enforced only once a public key is listed in `TRUSTED_KEYS`** in `core/updater/signature.py`; until then updates behave as before.

1. Once: `python build_tools/sign_release.py --generate release-signing.key`. Keep that file offline (never in the repository or CI) and back it up. Paste the printed public key into `TRUSTED_KEYS`.
2. For each release, after the build: `python build_tools/sign_release.py <version-folder> --key release-signing.key`. This writes `release.json.sig`, and `publish_release.py` verifies it and uploads it with the other assets.
3. To rotate a key, ship a release that lists both the old and the new public keys before retiring the old one.

Clients that predate this feature do not verify signatures; they must update once to get the check.

## Pull requests

- Keep changes focused; one concern per pull request.
- Describe what changed and how you verified it (tests, replay, live battle).
- Include `game.log` excerpts when fixing a bug, with personal information removed.
- Code adapted from other mods must keep its credit and licence (the project is GPL-3.0; see `LICENCE`).
