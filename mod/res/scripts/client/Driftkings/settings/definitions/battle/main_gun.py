# -*- coding: utf-8 -*-
from Driftkings._constants import MAIN_GUN
from Driftkings.settings.controls_schema import control
from Driftkings.settings.definitions.base import SectionDefinition


class MainGunSettings(SectionDefinition):
    NAME = MAIN_GUN.NAME

    TRANSLATED_TITLE = False
    COLUMNS = (
        (
            control(MAIN_GUN.BACK_GROUND_ENABLED),
            control(MAIN_GUN.TEXT_LOCK),
        ),
        (
        ),
    )
