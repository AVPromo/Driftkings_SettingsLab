# Packaged Wwise banks

Add matching `<name>.bnk` and `<name>.xml` files here. The XML must list `<name>.bnk` in `<loadBanks><bank><name>…</name></bank></loadBanks>`. Declare both files in `build_data/components.json`; the sound bank loader discovers the packaged XML. Keep each file below the updater inventory's `MAX_FILE` limit.

The installer changes JSON settings only; it never installs optional loose sound banks. `res/sound_bank_wwise` is the source Wwise project, not distribution content. `assets.exclude` excludes this README from packages.
