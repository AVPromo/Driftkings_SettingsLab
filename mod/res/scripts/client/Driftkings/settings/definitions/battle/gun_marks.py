# -*- coding: utf-8 -*-
from Driftkings._constants import MARKS_ON_GUN_BATTLE
from Driftkings.common import color_tables
from Driftkings.settings.controls_schema import control, hotkey, options, field
from Driftkings.settings.definitions.base import SectionDefinition


class MarksOnGunBattleSettings(SectionDefinition):
    NAME = MARKS_ON_GUN_BATTLE.NAME

    TRANSLATED_TITLE = False

    def normalize_changes(self, values, changes):
        panel = values.get(MARKS_ON_GUN_BATTLE.PANEL)
        if panel is not None:
            panel.pop('text', None)
            for key in ('x', 'y', 'alpha', 'height', 'width'):
                if key in panel:
                    panel[key] = float(panel[key])
        return values

    def getControlColumns(self):
        return (
            [
                options(MARKS_ON_GUN_BATTLE.COLOR_RATING, [table['ScaleColor'] for table in color_tables]),
                field(['gameface', 'enabled'], self.i18n['UI_mog_enableBattle']),
                control('showMarks'), control('showDelta'), control('showDamage'),
                control('showProgress'), control('showTargets'),
                control(MARKS_ON_GUN_BATTLE.SHOW_IN_STATISTIC),
                control(MARKS_ON_GUN_BATTLE.SHOW_IN_REPLAY),
                control(MARKS_ON_GUN_BATTLE.SHOW_IN_BATTLE),
                control(MARKS_ON_GUN_BATTLE.BACKGROUND),
            ],
            [
                field(['gameface', 'locked'], self.i18n['UI_mog_lockPosition']),
                field(['panel', 'x'], 'X', 'Slider', -7680.0, 7680.0, step=1.0),
                field(['panel', 'y'], 'Y', 'Slider', -4320.0, 4320.0, step=1.0),
                field([MARKS_ON_GUN_BATTLE.BATTLE_MESSAGE_SIZE_IN_PERCENT], self.i18n['UI_mog_scale'], 'Slider', 10, 1000, step=10),
                field(['gameface', 'backgroundOpacity'], self.i18n['UI_mog_opacity'], 'Slider', 0.0, 1.0, step=0.05),
                field(['gameface', 'accentColor'], self.i18n['UI_mog_accent'], 'ColorChoice'),
                field(['gameface', 'showTargetDamage'], self.i18n['UI_mog_target']),
                field(['gameface', 'showRequiredDamage'], self.i18n['UI_mog_needed']),
                hotkey(MARKS_ON_GUN_BATTLE.BUTTON_RESET),
                hotkey(MARKS_ON_GUN_BATTLE.BUTTON_SIZE_UP),
                hotkey(MARKS_ON_GUN_BATTLE.BUTTON_SIZE_DOWN)
            ]
        )
