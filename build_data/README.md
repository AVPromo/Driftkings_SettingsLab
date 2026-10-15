# Build data contract (schema 1)

These files describe the compiler in `build_tools/compiler.py`; editing them
does not compile or deploy the mod. See `build_tools/README.md` for commands.
All JSON uses UTF-8, two-space indentation and LF. Repository and archive paths
use `/`. Resolve repository paths from the project root, never from the current
working directory. Only `game.root`, `reference.root` and snapshot provenance
contain machine-specific paths.

## Files

| File | Responsibility |
| --- | --- |
| `build_config.json` | Game target, reference sources, Python compilation, archive, defaults, dependencies and generators |
| `components/*.json` | Feature entrypoints, default files and resource ownership |
| `locales.json` | Supported bundled languages and target version |
| `obfuscation.json` | Opt-in protected-bytecode policy; paths relative to `path_root` |
| `defaults_snapshot.json` | Imported NA defaults inventory and source/repository SHA-256 hashes |
| `patches/carousel_2.4.1.json` | Exact, ordered carousel bundle replacements with input/output hashes |
| `release.json` | Canonical version source, repository, package identity and changelog |
| `toolchain.example.json` | Template for the ignored `toolchain.local.json` path overrides |

## Component manifests

Every manifest has the same seven fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `id` | Filename stem and stable component identifier |
| `kind` | `feature` or `shared` |
| `enabled` | Boolean controlling startup and inclusion of owned assets |
| `entrypoint` | Feature module relative to `Driftkings`, or `null` for shared infrastructure |
| `config_files` | Exact paths relative to `defaults.source_root`; includes disabled-feature defaults |
| `assets` | List of `{ "source": ..., "target": ..., "generator": ... }` |

`source` is a repository path; `target` is a path **inside the WOTMOD**.
`generator` is `null` for checked-in assets, or a key in `generators` for outputs
that must be produced before packaging. C# generators declare both `output`
(executable) and `metadata` (`helper.json`), and either may be referenced by an
asset. The only wildcard is a trailing `/**`
on both source and target. It recursively preserves relative filenames and
applies `assets.exclude`. Empty selections, escaping paths and duplicate archive
targets, including case-only collisions, are errors.

All Python sources under `python.source_root` are compiled once to Python 2.7
bytecode. `python.archive_root` defines the archive prefix; shared imports are
included even when a startup feature is disabled. Manifests no longer repeat
intermediate `.pyc` paths. Enabled feature entrypoints, sorted lexically, define
`Driftkings/component_list.py`. The validator currently checks the checked-in list;
the compiler generates its own staged list before compilation without changing
the checked-in source.

`common`, `stats`, `ui` and `DKModSettings` are shared resource/infrastructure
groups. They do not create additional startup components. The battle SWF is owned
by `ui`; the SixthSense bank and XML are both owned by `SixthSense`.

## Defaults

`res/configs/Driftkings` contains `load.json` and the `default` profile imported
from `D:/Games/World_of_Tanks_NA/mods/configs/Driftkings`. Values are preserved
except carousel icon paths, which now address packaged resources under
`gui/maps/Driftkings/Carroucel/`. The old repository-only carousel preset was
removed because it is absent from the selected source profile.

Caches, `*.bak`, personal `.settings` preferences and language overrides are not
distribution defaults. The legacy single minimap JSON is retained alongside the
split documents because it exists in the requested source profile.

Defaults are a **separate installation payload**, outside the WOTMOD. A new
installation copies them to `mods/configs/Driftkings`; updates use `missing_only`
and preserve existing user settings. Bundled Python fallback defaults remain in
`settings/settings_data.py`; they are not another copy of the imported NA profile.
If repository defaults are edited, update their `sha256` values in the snapshot;
retain `source_sha256` as provenance of the imported originals.

## Compiler order

1. Validate this contract and allow explicit local overrides for game/reference
   roots. Treat both roots as read-only. The NA installation is version 2.4.1.0;
   the EU source reference and Flash libraries are version 2.4.1.5488.
2. Generate the enabled component list and compile all runtime modules using a
   real Python 2.7 host. Python 3 is for build tooling only.
3. Compile the battle Flash entrypoint using the declared source paths and
   pinned SWCs. Produce `build/flash/DriftkingsBattle.swf`.
4. Read the carousel bundle from the declared game packages, verify the source
   hash, apply each replacement only when its occurrence count matches, verify
   the output hash, then write `build/gameface/carousel/bundle.js`. The current
   patch is verified against **NA 2.4.1.0 build 970**; reject another bundle until
   reviewed. It is not a universal patch for all realms/builds.
5. Apply the optional obfuscation policy only for a protected build.
6. Package resolved bytecodes and enabled assets in `Driftkings.wotmod` using
   ZIP_STORED. Never package defaults, raw Python sources or external game files
   beyond the explicitly declared patched resource.
7. Produce a separate defaults payload and copy the two pinned UI dependency
   WOTMODs separately into the selected version's `mods` directory. Installation
   and game deployment are separate from building.

The compiler also builds both native C# helpers and their hash metadata. It
verifies the package before promoting it to the version/channel output folder.
Standalone data validation does not generate outputs or launch the game.

## Validation

From the repository root, using Python 3.10 or newer:

```powershell
python build_tools/validate_build_data.py
python build_tools/validate_build_data.py --check-game --write-plan build/build_plan.json
python -m unittest discover -s build_tools/tests -p "test_*.py"
```

`--check-game` reads the configured game packages and applies the carousel patch
in memory. `--check-generated` additionally requires the Flash and patched bundle
outputs to exist; it should fail before those generators have run. The plan is
for compiler development, not evidence of a completed build or in-game testing.
