# -*- coding: utf-8 -*-
from Driftkings._constants import PENETRATION_INDICATOR
from Driftkings.settings.controls_schema import control
from Driftkings.settings.definitions.base import SectionDefinition


class PenetrationIndicatorSettings(SectionDefinition):
    NAME = PENETRATION_INDICATOR.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(PENETRATION_INDICATOR.DISPLAY_ON_ALLIES),
        ),
        (
        ),
    )
