# -*- coding: utf-8 -*-
from Driftkings._constants import MARKS_ON_GUN_HANGAR
from Driftkings.settings.controls_schema import control, metadata, options, slider, field
from Driftkings.settings.definitions.base import SectionDefinition


class MarksOnGunHangarSettings(SectionDefinition):
    NAME = MARKS_ON_GUN_HANGAR.NAME

    TRANSLATED_TITLE = False

    def normalize_changes(self, values, changes):
        panel = values[MARKS_ON_GUN_HANGAR.PANEL]
        for setting, axis in (('positionX', 'x'), ('positionY', 'y')):
            if setting in changes:
                panel[axis] = float(values.pop(setting))
        return values

    def getControlColumns(self):
        x_color_key = 'UI_setting_colorRating_'
        x_color_list = ('NoobMeter', 'XVM', 'WotLabs')
        return (
            [
                control(MARKS_ON_GUN_HANGAR.SHOW_IN_HANGAR),
                control(MARKS_ON_GUN_HANGAR.SHOW_IN_STATISTIC),
                options(MARKS_ON_GUN_HANGAR.GOAL_SELECTION, [self.i18n['UI_panel_' + key] for key in ('automatic', 'goal1', 'goal2', 'goal3')]),
                control(MARKS_ON_GUN_HANGAR.COMPACT_MODE),
                options(MARKS_ON_GUN_HANGAR.COLOR_RATING, [self.i18n[x_color_key + x] for x in x_color_list])
            ],
            [
                control(MARKS_ON_GUN_HANGAR.SHOW_TOOLTIP_TARGETS),
                control(MARKS_ON_GUN_HANGAR.TEXT_LOCK),
                field(['gameface', 'scale'], self.i18n['UI_mog_scale'], 'Slider', 0.25, 2.0, step=0.05),
                field(['card', 'backgroundAlpha'], self.i18n['UI_mog_opacity'], 'Slider', 0.0, 1.0, step=0.05),
                field(['card', 'accentColor'], self.i18n['UI_mog_accent'], 'ColorChoice'),
                field(['gameface', 'showVehicleInfo'], self.i18n['UI_mog_vehicle']),
                field(['gameface', 'showProgress'], self.i18n['UI_mog_progress']),
                field(['gameface', 'showDamageStatistics'], self.i18n['UI_mog_damage']),
                field(['gameface', 'showMilestones'], self.i18n['UI_mog_milestones']),
                field(['gameface', 'showHistory'], self.i18n['UI_mog_history']),
                field(['gameface', 'showAdvancedStatistics'], self.i18n['UI_mog_advanced']),
                slider(MARKS_ON_GUN_HANGAR.HISTORY_BATTLES, 1, 20, 1),
                metadata(slider('positionX', -7680, 7680, 1, value=self.data[MARKS_ON_GUN_HANGAR.PANEL]['x']), path=[MARKS_ON_GUN_HANGAR.PANEL, 'x']),
                metadata(slider('positionY', -4320, 4320, 1, value=self.data[MARKS_ON_GUN_HANGAR.PANEL]['y']), path=[MARKS_ON_GUN_HANGAR.PANEL, 'y'])
            ]
        )
