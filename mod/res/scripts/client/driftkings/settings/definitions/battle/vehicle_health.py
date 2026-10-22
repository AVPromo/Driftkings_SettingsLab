# -*- coding: utf-8 -*-
from driftkings._constants import GLOBAL, VEHICLE_HEALTH
from driftkings.settings.controls_schema import slider
from driftkings.settings.definitions.base import SectionDefinition


class VehicleHealthSettings(SectionDefinition):
    NAME = VEHICLE_HEALTH.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            slider(GLOBAL.X, -2000, 2000, 1, '{{value}}%s' % ' px'),
            slider(GLOBAL.Y, -2000, 2000, 1, '{{value}}%s' % ' px'),
        ),
        (
        ),
    )
