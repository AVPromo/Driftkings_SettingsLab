# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_STATISTICS
from Driftkings.common.utils.colorRatting import color_tables
from Driftkings.settings.controls_schema import control, options
from Driftkings.settings.definitions.base import SectionDefinition


class BattleStatisticsSettings(SectionDefinition):
    NAME = BATTLE_STATISTICS.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            options(BATTLE_STATISTICS.COLOR_RATING, [table['ScaleColor'] for table in color_tables]),
            control(BATTLE_STATISTICS.FORMAT, 'TextInput', width=300),
        ),
        (
        ),
    )
