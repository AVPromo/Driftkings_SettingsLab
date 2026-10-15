# -*- coding: utf-8 -*-
from Driftkings._constants import LOGS_SWAPPER
from Driftkings.settings.controls_schema import control
from Driftkings.settings.definitions.base import SectionDefinition


class LogsSwapperSettings(SectionDefinition):
    NAME = LOGS_SWAPPER.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(LOGS_SWAPPER.LOG_SWAPPER),
            control(LOGS_SWAPPER.WG_LOG_HIDE_CRITICS),
            control(LOGS_SWAPPER.WG_LOG_HIDE_BLOCK),
            control(LOGS_SWAPPER.WG_LOG_HIDE_ASSIST),
        ),
        (
        ),
    )
