# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_ALIASES
from Driftkings.settings.definitions.battle.own_health import OwnHealthSettings as Settings
from Driftkings.views.battle.own_health import OwnHealth

AS_BATTLE = BATTLE_ALIASES.OWN_HEALTH
config = Settings()


def getBattleViews():
    return ((AS_BATTLE, OwnHealth, config),)
