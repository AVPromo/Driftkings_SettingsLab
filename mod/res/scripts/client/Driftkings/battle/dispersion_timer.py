# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_ALIASES
from Driftkings.settings.definitions.battle.dispersion_timer import DispersionTimerSettings as Settings
from Driftkings.views.battle.dispersion_timer import DispersionTimer

AS_BATTLE = BATTLE_ALIASES.DISPERSION_TIMER
config = Settings()


def getBattleViews():
    return ((AS_BATTLE, DispersionTimer, config),)
