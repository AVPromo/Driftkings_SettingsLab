# -*- coding: utf-8 -*-
from Driftkings._constants import ARMOR_CALCULATOR
from Driftkings.settings.controls_schema import control
from Driftkings.settings.definitions.base import SectionDefinition


class ArmorCalculatorSettings(SectionDefinition):
    NAME = ARMOR_CALCULATOR.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(ARMOR_CALCULATOR.DISPLAY_ON_ALLIES),
        ),
        (
        ),
    )
