# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_STAT
from Driftkings.common import color_tables
from Driftkings.settings.controls_schema import control, options
from Driftkings.settings.definitions.base import SectionDefinition


class BattleStatSettings(SectionDefinition):
    NAME = BATTLE_STAT.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            options(BATTLE_STAT.COLOR_RATING, [table['ScaleColor'] for table in color_tables]),
            control(BATTLE_STAT.FORMAT, 'TextInput', width=300),
        ),
        (
        ),
    )
