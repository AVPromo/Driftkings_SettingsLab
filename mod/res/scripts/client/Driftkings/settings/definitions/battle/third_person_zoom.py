# -*- coding: utf-8 -*-
from Driftkings._constants import THIRD_PERSON_ZOOM
from Driftkings.settings.controls_schema import slider
from Driftkings.settings.definitions.base import SectionDefinition


class ThirdPersonZoomSettings(SectionDefinition):
    NAME = THIRD_PERSON_ZOOM.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            slider(THIRD_PERSON_ZOOM.SCROLL_SENSITIVITY, 1.0, 100.0, 1.0, '{{value}}'),
            slider(THIRD_PERSON_ZOOM.MIN, 1.0, 450.0, 1.0, '{{value}} m'),
        ),
        (
            slider(THIRD_PERSON_ZOOM.START_DEAD_DIST, 10.0, 100.0, 5.0, '{{value}} m'),
            slider(THIRD_PERSON_ZOOM.MAX, 10.0, 450.0, 10.0, '{{value}} m'),
        ),
    )

    def normalize_changes(self, values, changes):
        if values[THIRD_PERSON_ZOOM.MIN] > values[THIRD_PERSON_ZOOM.MAX]:
            raise ValueError('Minimum camera distance cannot exceed maximum camera distance')
        return values
