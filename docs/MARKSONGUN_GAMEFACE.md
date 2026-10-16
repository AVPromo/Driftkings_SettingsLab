# MarksOnGun Gameface panels

Introduced in 0.1.2-beta.3 for WoT 2.4.1.0.

## Organization

- `core/marks_calculator.py`: shared pure calculations; combined damage is direct damage plus the greatest assistance category, not the sum of assistance types.
- `core/marks_state.py`: independent battle/hangar snapshots with change notifications.
- `battle/gun_marks.py`: battle feedback, friendly-damage correction and own-account calibration cache.
- `lobby/gun_marks.py`: current-vehicle dossier, tooltips and bounded observed history.
- `views/battle/gun_marks.py`: owned child of the native RandomHUDView, cursor/visibility events and position persistence.
- `views/hangar/gun_marks.py`: owned hangar child and position persistence.
- `gui/gameface/mods/Driftkings/shared/marks_panel.*`: shared presentation, model binding and drag lifecycle.
- `MarksOnGunBattle` and `MarksOnGunHangar`: Compact and Full presentations respectively.

The Flash MarksCard and legacy HTML templates/presets are removed. Other features continue to use the shared Flash overlay where required. Interface resources are registered in the interface catalog and build manifests.

## Configuration

Canonical JSON defaults are in `res/configs/Driftkings/default/`.

Battle uses `battleMessageSizeInPercent` (100 = normal size), `panel` for position/alignment, and `gameface` for accent, opacity, target visibility and position lock. Missing defaults are supplied by the central settings manager. Personal files remain authoritative.

Disable `gameface.locked` to drag the battle header while the native cursor is visible, normally with left Ctrl. The hangar uses `textLock`, `gameface.scale`, `card` colors/opacity, and `panel` position. Dragging the hangar header uses the left mouse button without Ctrl.

Both contexts capture mouse events before nested/native handlers interrupt bubbling. Movement stays within the viewport and position is saved through the central settings service on release. Locking, hiding or disposing a panel cancels dragging. All listeners and model subscriptions are removed on disposal. Temporary click/layout diagnostics are excluded from this beta.

## Data and limitations

Battle estimates use the existing EMA/calibration algorithm and milestone thresholds 65%, 85% and 95%. Hangar targets retain the existing proportional EMA estimate; they are estimates rather than guaranteed next-battle damage thresholds.

History contains only observed dossier samples, indexed by the real battle counter. A replay without valid own-account calibration shows unavailable values. No sample data or other-account cache is used as a fallback.

## Validation

Local checks covered calculation regression, max-assistance semantics, friendly damage, settings persistence, lifecycle cleanup and dragging. Python 2.7 compilation, protected import validation and package generation passed. Tests and generated artifacts are local and excluded from Git.

The user confirmed panel dragging on NA in the hangar and battle replay. Live-battle estimate accuracy, all realms and the full in-game updater flow still require client validation.
