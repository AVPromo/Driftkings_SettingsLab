# -*- coding: utf-8 -*-
from driftkings._constants import ARTILLERY_BLAST_RADIUS
from driftkings.settings.controls_schema import control, hotkey
from driftkings.settings.definitions.base import SectionDefinition


class ArtilleryBlastRadiusSettings(SectionDefinition):
    NAME = ARTILLERY_BLAST_RADIUS.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(ARTILLERY_BLAST_RADIUS.SHOW_SPLASH_ON_DEFAULT),
            control(ARTILLERY_BLAST_RADIUS.SHOW_DOT_ON_DEFAULT),
            control(ARTILLERY_BLAST_RADIUS.SHOW_MODE_ARCADE),
            control(ARTILLERY_BLAST_RADIUS.SHOW_MODE_SNIPER),
            control(ARTILLERY_BLAST_RADIUS.SHOW_MODE_ARTY),
        ),
        (
            hotkey(ARTILLERY_BLAST_RADIUS.BUTTON_SHOW_SPLASH),
            hotkey(ARTILLERY_BLAST_RADIUS.BUTTON_SHOW_DOT),
        ),
    )
