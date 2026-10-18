# Installer images

Images are optional and supplied separately. Missing branding uses Inno's built-in images and icon; missing previews show no image. The validator reports missing branding as warnings.

Target/compiler tested: **Inno Setup 6.7.1** (minimum 6.7.1). Paths:

- `branding/setup-icon.ico`: include 16, 32, 48, 64 and 256 px icon sizes.
- `branding/wizard-large.bmp`: welcome/finished image, aspect ratio **164:314**. Inno 6.7 defaults allocate about **202x386** at 100% DPI; prefer **430x824** or larger for high DPI. The built-in image is 240x459.
- `branding/wizard-small.bmp`: square header image; about **58x58** at 100% DPI. Prefer **147x147** or larger.
- `previews/<canonical_component_key>.png`: optional preview, e.g. `sixth_sense_alert.png`. A **600x360** image works well; the wizard fits it proportionally inside its preview area. No preview is installed into the game.

Inno 6.7.1 accepts PNG for wizard branding, including transparency. You may use `wizard-large.png` / `wizard-small.png` instead of BMP; BMP takes precedence if both exist. The setup icon must remain ICO. Keep images within the updater's `MAX_FILE` limit. Tracked `.gitkeep` files only keep empty directories in Git and are not packaged.

Replace the files and rebuild: `python build_tools/build_installer.py --artifacts build/debug/beta/0.1.2-beta.4 --compile`. No script edits are needed.

Official documentation: [large image](https://jrsoftware.org/ishelp/topic_setup_wizardimagefile.htm), [small image](https://jrsoftware.org/ishelp/topic_setup_wizardsmallimagefile.htm), [icon](https://jrsoftware.org/ishelp/topic_setup_setupiconfile.htm), [PNG preview classes](https://jrsoftware.org/ishelp/topic_scriptclasses.htm).

Guia em português, com caminhos e exemplos: [GUIA_INSTALADOR_PT.md](../GUIA_INSTALADOR_PT.md).
