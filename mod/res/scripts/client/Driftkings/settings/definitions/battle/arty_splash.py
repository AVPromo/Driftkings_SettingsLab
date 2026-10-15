# -*- coding: utf-8 -*-
from Driftkings._constants import ARTY_SPLASH
from Driftkings.settings.controls_schema import control, hotkey
from Driftkings.settings.definitions.base import SectionDefinition


class ArtySplashSettings(SectionDefinition):
    NAME = ARTY_SPLASH.NAME

    TRANSLATED_TITLE = False
    COLUMNS = (
        (
            control(ARTY_SPLASH.SHOW_SPLASH_ON_DEFAULT),
            control(ARTY_SPLASH.SHOW_DOT_ON_DEFAULT),
            control(ARTY_SPLASH.SHOW_MODE_ARCADE),
            control(ARTY_SPLASH.SHOW_MODE_SNIPER),
            control(ARTY_SPLASH.SHOW_MODE_ARTY),
        ),
        (
            hotkey(ARTY_SPLASH.BUTTON_SHOW_SPLASH),
            hotkey(ARTY_SPLASH.BUTTON_SHOW_DOT),
        ),
    )
