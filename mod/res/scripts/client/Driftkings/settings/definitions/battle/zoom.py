# -*- coding: utf-8 -*-
from Driftkings._constants import ZOOM_EXTENDED
import math

from Driftkings.settings.controls_schema import control, slider, field
from Driftkings.settings.definitions.base import SectionDefinition


class ZoomExtendedSettings(SectionDefinition):
    NAME = ZOOM_EXTENDED.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(ZOOM_EXTENDED.NO_BINOCULARS),
            control(ZOOM_EXTENDED.NO_FLASH_BANG),
            control(ZOOM_EXTENDED.NO_SHOCK_WAVE),
            control(ZOOM_EXTENDED.NO_SNIPER_DYNAMIC),
        ),
        (
            control(ZOOM_EXTENDED.DISABLE_CAM_AFTER_SHOT),
            slider(ZOOM_EXTENDED.DISABLE_CAM_AFTER_SHOT_LATENCY, 0.0, 20.0, 0.1, '{{value}} s'),
            control(ZOOM_EXTENDED.DISABLE_CAM_AFTER_SHOT_SKIP_CLIP),
        ),
    )

    def getControlColumns(self):
        columns = [list(column) for column in self.COLUMNS]
        columns[1].extend((
            field(['zoomSteps', 'enabled'], self.i18n['UI_setting_zoomSteps_enabled_text']),
            field(['zoomSteps', 'steps'], self.i18n['UI_setting_zoomSteps_steps_text'],
                  kind='TextInput', jsonValue=True,
                  tooltip=self.i18n['UI_setting_zoomSteps_steps_tooltip']),
        ))
        return columns

    def normalize_changes(self, values, changes):
        steps = values['zoomSteps']['steps']
        if not isinstance(steps, list) or len(steps) < 4:
            raise ValueError('Zoom requires at least four levels')
        if any(type(step) not in (int, float) or math.isnan(step) or
               math.isinf(step) or step < 2.0 for step in steps):
            raise ValueError('Zoom levels must be finite numbers of at least 2.0')
        if len(set(steps)) != len(steps):
            raise ValueError('Zoom levels must be unique')
        values['zoomSteps']['steps'] = sorted(float(step) for step in steps)
        return values
