# -*- coding: utf-8 -*-
from Driftkings._constants import FLIGHT_TIMER, GLOBAL
from Driftkings.settings.controls_schema import control, slider
from Driftkings.settings.definitions.base import SectionDefinition


class FlightTimerSettings(SectionDefinition):
    NAME = FLIGHT_TIMER.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(FLIGHT_TIMER.TEMPLATE, 'TextInput', 400),
            control(FLIGHT_TIMER.SPG_ONLY),
        ),
        (
            slider(GLOBAL.X, -2000, 2000, 1, '{{value}}%s' % ' X'),
            slider(GLOBAL.Y, -2000, 2000, 1, '{{value}}%s' % ' Y'),
        ),
    )
