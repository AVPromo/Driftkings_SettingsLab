# -*- coding: utf-8 -*-
from Driftkings._constants import ARCADE_ZOOM
from Driftkings.settings.controls_schema import slider
from Driftkings.settings.definitions.base import SectionDefinition


class ArcadeZoomSettings(SectionDefinition):
    NAME = ARCADE_ZOOM.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            slider(ARCADE_ZOOM.SCROLL_SENSITIVITY, 1.0, 100.0, 1.0, '{{value}} %'),
            slider(ARCADE_ZOOM.MIN, 1.0, 450.0, 1.0, '{{value}} m'),
        ),
        (
            slider(ARCADE_ZOOM.START_DEAD_DIST, 10.0, 100.0, 5.0, '{{value}} %'),
            slider(ARCADE_ZOOM.MAX, 10.0, 450.0, 10.0, '{{value}} m'),
        ),
    )
