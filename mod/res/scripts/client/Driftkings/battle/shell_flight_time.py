# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_ALIASES
from Driftkings.settings.definitions.battle.shell_flight_time import ShellFlightTimeSettings as Settings
from Driftkings.views.battle.shell_flight_time import FlightTime

AS_BATTLE = BATTLE_ALIASES.SHELL_FLIGHT_TIME
config = Settings()


def getBattleViews():
    return ((AS_BATTLE, FlightTime, config),)
