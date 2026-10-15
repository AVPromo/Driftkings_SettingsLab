# Regional languages

Each `<code>.py` contains the component translations in `TEXT` and the settings
panel translations in `PANEL`. The panel loader is `i18n/panel.py`; there are no
translation catalogs under `settings/panel`. Existing user overrides in
`<settings root>/locales/<code>.json` continue to work.

The shared registry is `Driftkings/locale_support.py`. Both the panel and component
catalogs use its normalization. `build_data/locales.json` records the regional
language lists, source URLs, verification date and translation coverage.

The Wargaming portal selectors list:

- EU: Czech, German, English, Spanish, French, Hungarian, Italian, Polish,
  Russian, Turkish and Ukrainian.
- NA: English, Latin American Spanish and Brazilian Portuguese.
- ASIA: English, Japanese, Korean, Thai, Vietnamese, Simplified Chinese
  (Singapore) and Traditional Chinese.

These are portal language lists, not a guarantee that each regional client
distributes every corresponding language pack. Spanish and Portuguese regional
variants reuse the existing `es` and `pt` catalogs. `zh-SG` resolves to `zh_cn`;
`zh-TW` and `zh-HK` resolve to `zh_tw`. The Chinese scripts stay separate.

All 18 catalogs contain the same 909 component keys and 160 panel keys as
`en.py`. Missing entries and prose still in English were completed with machine
translation. Existing localized text was preserved. New translations need
native-speaker review; complete key coverage is not a linguistic quality rating.

`python build_tools/validate_locales.py` checks exact key coverage, value types,
nonempty strings, formatting macros, HTML and colors. The compiler runs this
validation before building. Add new English keys to every catalog in the same
change. Names and identifiers may legitimately be identical across languages.
The loader retains the English fallback and user JSON overrides.
