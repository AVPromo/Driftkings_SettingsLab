# -*- coding: utf-8 -*-
from driftkings._constants import GAME_LOG_MANAGER
from driftkings.settings.controls_schema import control
from driftkings.settings.definitions.base import SectionDefinition


class GameLogManagerSettings(SectionDefinition):
    NAME = GAME_LOG_MANAGER.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(GAME_LOG_MANAGER.LOG_SWAPPER),
            control(GAME_LOG_MANAGER.WG_LOG_HIDE_CRITICS),
            control(GAME_LOG_MANAGER.WG_LOG_HIDE_BLOCK),
            control(GAME_LOG_MANAGER.WG_LOG_HIDE_ASSIST),
        ),
        (
        ),
    )
