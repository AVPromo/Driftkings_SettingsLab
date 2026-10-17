# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_ALIASES
from Driftkings.settings.definitions.battle.vehicle_health import VehicleHealthSettings as Settings
from Driftkings.views.battle.vehicle_health import OwnHealth

AS_BATTLE = BATTLE_ALIASES.VEHICLE_HEALTH
config = Settings()


def getBattleViews():
    return ((AS_BATTLE, OwnHealth, config),)
