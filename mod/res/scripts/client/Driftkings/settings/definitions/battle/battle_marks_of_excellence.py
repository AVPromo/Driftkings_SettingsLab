# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_MARKS_OF_EXCELLENCE
from Driftkings.common import color_tables
from Driftkings.settings.controls_schema import control, hotkey, options, field
from Driftkings.settings.definitions.base import SectionDefinition


class BattleMarksOfExcellenceSettings(SectionDefinition):
    NAME = BATTLE_MARKS_OF_EXCELLENCE.NAME

    TRANSLATED_TITLE = True

    def normalize_changes(self, values, changes):
        panel = values.get(BATTLE_MARKS_OF_EXCELLENCE.PANEL)
        if panel is not None:
            panel.pop('text', None)
            for key in ('x', 'y', 'alpha', 'height', 'width'):
                if key in panel:
                    panel[key] = float(panel[key])
        return values

    def getControlColumns(self):
        return (
            [
                options(BATTLE_MARKS_OF_EXCELLENCE.COLOR_RATING, [table['ScaleColor'] for table in color_tables]),
                field(['gameface', 'enabled'], self.i18n['UI_mog_enableBattle']),
                field(['gameface', 'miniMode'], self.i18n['UI_mog_miniMode']),
                control('showMarks'), control('showDelta'), control('showDamage'),
                control('showProgress'), control('showTargets'),
                control(BATTLE_MARKS_OF_EXCELLENCE.SHOW_IN_STATISTIC),
                control(BATTLE_MARKS_OF_EXCELLENCE.SHOW_IN_REPLAY),
                control(BATTLE_MARKS_OF_EXCELLENCE.SHOW_IN_BATTLE),
                control(BATTLE_MARKS_OF_EXCELLENCE.BACKGROUND),
            ],
            [
                field(['gameface', 'locked'], self.i18n['UI_mog_lockPosition']),
                field(['panel', 'x'], 'X', 'Slider', -7680.0, 7680.0, step=1.0),
                field(['panel', 'y'], 'Y', 'Slider', -4320.0, 4320.0, step=1.0),
                field([BATTLE_MARKS_OF_EXCELLENCE.BATTLE_MESSAGE_SIZE_IN_PERCENT], self.i18n['UI_mog_scale'], 'Slider', 10, 1000, step=10),
                field(['gameface', 'backgroundOpacity'], self.i18n['UI_mog_opacity'], 'Slider', 0.0, 1.0, step=0.05),
                field(['gameface', 'accentColor'], self.i18n['UI_mog_accent'], 'ColorChoice'),
                field(['gameface', 'showTargetDamage'], self.i18n['UI_mog_target']),
                field(['gameface', 'showRequiredDamage'], self.i18n['UI_mog_needed']),
                hotkey(BATTLE_MARKS_OF_EXCELLENCE.BUTTON_RESET),
                hotkey(BATTLE_MARKS_OF_EXCELLENCE.BUTTON_SIZE_UP),
                hotkey(BATTLE_MARKS_OF_EXCELLENCE.BUTTON_SIZE_DOWN)
            ]
        )
