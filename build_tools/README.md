# Driftkings compiler

Python 3.10+ orchestrates the build. Runtime sources are compiled by a real
Python 2.7 interpreter, or SourceTree's Python 2.7 Mercurial host. Game and
reference directories are read-only inputs. Building never installs files into
the game, starts it, creates Git tags or publishes to GitHub.

## Commands

Run from the repository root:

```powershell
# Inspect the version, channel, tools and output path without compiling.
python build_tools/compiler.py --plan

# Debug build using the current global mod version.
.\debug.cmd

# Protected release build using the current global mod version.
.\release.cmd

# Explicit beta or stable version; the channel is derived from SemVer.
.\release.cmd --version 0.1.2-beta.2 --channel beta
.\release.cmd --version 0.1.2 --channel stable

# Diagnostic release layout without protection; excluded from publication.
.\release.cmd --no-obfuscation

# Optional changelog: UTF-8 text, one entry per line.
.\release.cmd --changelog build_data/changelog.txt
```

Direct Python equivalents use `--mode debug` or `--mode release`. The `.cmd`
wrappers accept the same remaining arguments and work from another directory.
Set `DK_PYTHON3` to a Python 3 executable path if `python` is not appropriate.

The canonical mod version is `Driftkings.VERSION`, currently `0.1.2-beta.1`.
`--version` overrides only the build's staged runtime and release artifacts;
it does not modify your sources or increment the project version automatically.
Beta/RC versions use the beta channel; plain `X.Y.Z` versions use stable.
The game version is a separate four-part value in `build_config.json`.

## Tools

Automatic discovery covers the local SourceTree host, standalone Python 2.7,
Flex under the neighboring `Programas/Flex` directory, Adobe Animate's
`playerglobal.swc`, Java 8, the Windows .NET Framework C# compiler, and PJOrion.
Explicit command-line options override `DK_*` environment variables, which
override `build_data/toolchain.local.json`, which overrides auto-discovery.

Copy `build_data/toolchain.example.json` to `build_data/toolchain.local.json`
to customize paths. The local file is ignored by Git. CLI options include
`--python27`, `--hg`, `--flex-home`, `--mxmlc-jar`, `--playerglobal`, `--java`,
`--csc`, `--pjorion-home` and `--game-root`. Executable options accept executable
paths, not shell commands. `DK_FLEX_HOME`, for example, overrides the SDK root.

Release builds honor `build_data/obfuscation.json`. With the current enabled
policy, only the three explicit allowlisted bytecodes may be protected.
PJOrion runs from a private build copy with its update/integration options
disabled; the installed tool configuration and original bytecodes are checked
for changes. Protected package imports are verified by Python 2.7 afterward.

An optional `obfuscator_command` argument array in the local toolchain file can
replace PJOrion. It must contain `{output}`; `{input}` is also available. It runs
without a shell and must preserve the input while modifying the protected output.
There is no silent fallback if protection fails. Debug builds do not require
protection; `--protect` enables it explicitly. `--no-obfuscation` marks an
otherwise protected release as diagnostic and not publishable.

## Outputs

Release outputs are under `build/releases/<channel>/<version>/`; debug outputs
are under `build/debug/<channel>/<version>/`:

| Artifact | Purpose |
| --- | --- |
| `Driftkings.wotmod` | Stored ZIP with Python 2.7 bytecodes, Flash, resources, native helpers and `meta.xml` |
| `release.json` | Schema 1 metadata consumed by the existing updater |
| `Driftkings-defaults.zip` | Your selected Driftkings defaults, separate from the WOTMOD |
| `dependencies/*.wotmod` | The two pinned external UI dependencies |
| `Driftkings-<version>-WoT-<game>.zip` | Distribution with `mods/<game>/`, a separate defaults ZIP and installation instructions |
| `build-report.json` | Tool paths, source hashes, Git revision, mode, protection status, counts and verification results |
| `SHA256SUMS.txt` | Checksums for the output files, including the build report |

New installations may extract the separate defaults ZIP. Existing installations
keep their `mods/configs/Driftkings` settings. The compiler does not change these
settings. The current in-game updater updates the unified WOTMOD only; dependency
and first-install-default distribution remain separate payloads.

Each invocation gets a fresh `build/runs/<id>/` directory containing logs,
compiled code and generated resources. Failed compilation/verification does not
replace an earlier version directory. Successful rebuilds preserve the earlier
directory under `build/previous/`. The latest validated WOTMOD is also copied to
`build/unified/Driftkings.wotmod`; generated files and unprotected staging aliases
are updated under the paths declared in the build contract.

The compiler generates the enabled component list in staging, compiles all Python
sources, compiles Flash and C#, generates the declared Gameface patch, packages
only declared resources, and validates ZIP inventory, Python bytecode headers,
SWF structure, native-helper hashes and updater metadata. Python 2.7 then loads
the actual packaged runtime version and selected updater/calculator modules.
When the optional local probe is present, it imports the packaged `common.utils` tree while the `common` facade is
incomplete and exercises its four deferred hooks with stubbed game services.
The same probe initializes configuration metadata through the compatibility
facade and resolves page-only and page/HUD battle layouts. These checks catch
startup dependency and layout errors without requiring a running game. Local
tests and this probe are not distributed; the report records `not-installed`
when the probe is absent. The package checks above still run.
Successful build verification is not in-game functional validation.

## GitHub releases

Publication is a separate command. Previewing performs no GitHub write:

```powershell
python build_tools/publish_release.py build/releases/beta/0.1.2-beta.1

# Explicit upload, creating a draft release.
python build_tools/publish_release.py build/releases/beta/0.1.2-beta.1 --publish

# Explicit upload and public release (pre-release for beta/RC).
python build_tools/publish_release.py build/releases/beta/0.1.2-beta.1 --publish --live
```

Uploading requires GitHub CLI authentication, unchanged artifact checksums and
a clean checkout at the commit recorded by the build. Commit and push your source
changes, then rebuild before publication. The command uses tag `v<version>`, the recorded
source commit, and the correct GitHub prerelease flag. It never replaces an
existing release or deletes tags. Repository and package identity are declared
in `build_data/release.json`.

## Checks

```powershell
python build_tools/validate_locales.py
python build_tools/validate_build_data.py --check-generated
```
