# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_ALIASES
from Driftkings.settings.definitions.battle.aiming_countdown import AimingCountdownSettings as Settings
from Driftkings.views.battle.aiming_countdown import DispersionTimer

AS_BATTLE = BATTLE_ALIASES.AIMING_COUNTDOWN
config = Settings()


def getBattleViews():
    return ((AS_BATTLE, DispersionTimer, config),)
