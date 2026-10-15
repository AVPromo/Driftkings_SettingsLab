# -*- coding: utf-8 -*-
from Driftkings._constants import SERVER_TURRET_EXTENDED
from Driftkings.settings.controls_schema import control, hotkey
from Driftkings.settings.definitions.base import SectionDefinition


class ServerTurretExtendedSettings(SectionDefinition):
    NAME = SERVER_TURRET_EXTENDED.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(SERVER_TURRET_EXTENDED.SERVER_TURRET),
            control(SERVER_TURRET_EXTENDED.FIX_ACCURACY_IN_MOVE),
            control(SERVER_TURRET_EXTENDED.FIX_WHEEL_CRUISE_CONTROL),
            control(SERVER_TURRET_EXTENDED.ACTIVATE_MESSAGE),
        ),
        (
            hotkey(SERVER_TURRET_EXTENDED.BUTTON_AUTO_MODE),
            hotkey(SERVER_TURRET_EXTENDED.BUTTON_MAX_MODE),
            control(SERVER_TURRET_EXTENDED.MAX_WHEEL_MODE),
            control(SERVER_TURRET_EXTENDED.AUTO_ACTIVATE_WHEEL_MODE),
        ),
    )
