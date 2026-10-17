# -*- coding: utf-8 -*-
from Driftkings._constants import HANGAR_MARKS_OF_EXCELLENCE
from Driftkings.settings.controls_schema import control, metadata, options, slider, field
from Driftkings.settings.definitions.base import SectionDefinition


class HangarMarksOfExcellenceSettings(SectionDefinition):
    NAME = HANGAR_MARKS_OF_EXCELLENCE.NAME

    TRANSLATED_TITLE = True

    def normalize_changes(self, values, changes):
        panel = values[HANGAR_MARKS_OF_EXCELLENCE.PANEL]
        for setting, axis in (('positionX', 'x'), ('positionY', 'y')):
            if setting in changes:
                panel[axis] = float(values.pop(setting))
        return values

    def getControlColumns(self):
        x_color_key = 'UI_setting_colorRating_'
        x_color_list = ('NoobMeter', 'XVM', 'WotLabs')
        return (
            [
                control(HANGAR_MARKS_OF_EXCELLENCE.SHOW_IN_HANGAR),
                control(HANGAR_MARKS_OF_EXCELLENCE.SHOW_IN_STATISTIC),
                options(HANGAR_MARKS_OF_EXCELLENCE.GOAL_SELECTION, [self.i18n['UI_panel_' + key] for key in ('automatic', 'goal1', 'goal2', 'goal3')]),
                control(HANGAR_MARKS_OF_EXCELLENCE.COMPACT_MODE),
                options(HANGAR_MARKS_OF_EXCELLENCE.COLOR_RATING, [self.i18n[x_color_key + x] for x in x_color_list])
            ],
            [
                control(HANGAR_MARKS_OF_EXCELLENCE.SHOW_TOOLTIP_TARGETS),
                control(HANGAR_MARKS_OF_EXCELLENCE.TEXT_LOCK),
                field(['gameface', 'scale'], self.i18n['UI_mog_scale'], 'Slider', 0.25, 2.0, step=0.05),
                field(['card', 'backgroundAlpha'], self.i18n['UI_mog_opacity'], 'Slider', 0.0, 1.0, step=0.05),
                field(['card', 'accentColor'], self.i18n['UI_mog_accent'], 'ColorChoice'),
                field(['gameface', 'showVehicleInfo'], self.i18n['UI_mog_vehicle']),
                field(['gameface', 'showProgress'], self.i18n['UI_mog_progress']),
                field(['gameface', 'showDamageStatistics'], self.i18n['UI_mog_damage']),
                field(['gameface', 'showMilestones'], self.i18n['UI_mog_milestones']),
                field(['gameface', 'showHistory'], self.i18n['UI_mog_history']),
                field(['gameface', 'showAdvancedStatistics'], self.i18n['UI_mog_advanced']),
                slider(HANGAR_MARKS_OF_EXCELLENCE.HISTORY_BATTLES, 1, 20, 1),
                metadata(slider('positionX', -7680, 7680, 1, value=self.data[HANGAR_MARKS_OF_EXCELLENCE.PANEL]['x']), path=[HANGAR_MARKS_OF_EXCELLENCE.PANEL, 'x']),
                metadata(slider('positionY', -4320, 4320, 1, value=self.data[HANGAR_MARKS_OF_EXCELLENCE.PANEL]['y']), path=[HANGAR_MARKS_OF_EXCELLENCE.PANEL, 'y'])
            ]
        )
