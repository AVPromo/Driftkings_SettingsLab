# -*- coding: utf-8 -*-
from driftkings._constants import BATTLE_PERFORMANCE
from driftkings.settings.controls_schema import control, options
from driftkings.settings.definitions.base import SectionDefinition


class BattlePerformanceSettings(SectionDefinition):
    NAME = BATTLE_PERFORMANCE.NAME

    TRANSLATED_TITLE = True

    def normalize_loaded(self, values):
        # Upgrade only the original shipped Flash template; keep custom macros.
        from driftkings.settings.default_values import DEFAULTS
        if values.get(BATTLE_PERFORMANCE.BATTLE_RESULTS_FORMAT) == "<textformat leading='-2' tabstops='[0, 300]'>\t<font color='#FFFFFF' size='15'>{mapName} - {battleType}    WN8:<font color='{c:wn8}'>{wn8}</font>|=|EFF:<font color='{c:eff}'>{eff}</font>|=|Xte:<font color='{c:xte}'>{xte}</font></font></textformat>":
            values[BATTLE_PERFORMANCE.BATTLE_RESULTS_FORMAT] = DEFAULTS[self.NAME][BATTLE_PERFORMANCE.BATTLE_RESULTS_FORMAT]
        return values

    def getControlColumns(self):
        x_color_key = 'UI_setting_colorRatting_'
        x_color_list = ('NoobMeter', 'XVM', 'WotLabs')
        return (
            [
                control(BATTLE_PERFORMANCE.TEXT_LOCK),
                options(BATTLE_PERFORMANCE.COLOR_RATTING, [self.i18n[x_color_key + x] for x in x_color_list]),
                control(BATTLE_PERFORMANCE.FORMAT, 'TextInput', 400)
            ],
            [
                control(BATTLE_PERFORMANCE.BATTLE_RESULTS_WINDOW),
                control(BATTLE_PERFORMANCE.BATTLE_RESULTS_FORMAT, 'TextInput', 400)
            ]
        )
