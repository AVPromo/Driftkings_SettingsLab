# -*- coding: utf-8 -*-
"""Server gun-angle synchronization; no vehicle movement or firing control."""
import math
import VehicleGunRotator
import gun_rotation_shared
from Driftkings._constants import GLOBAL, SERVER_TURRET_SYNC
from Driftkings.common.utils.game import sendPanelMessage
from Driftkings.common.utils import events
from Driftkings.core.callbacks import callback
from Driftkings.core.hooks import override, on_event
from Driftkings.settings.service import settings_service
from Driftkings.settings.definitions.battle.server_turret_sync import ServerTurretSyncSettings as Settings

config = Settings()


@override(VehicleGunRotator.VehicleGunRotator, 'setShotPosition')
def new__vehicleGunRotatorSetShotPosition(func, self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh=False):
    if settings_service.getComponentDict(config)[GLOBAL.ENABLED]:
        if self._avatar.vehicle and settings_service.getComponentDict(config)[SERVER_TURRET_SYNC.SERVER_TURRET]:
            self._VehicleGunRotator__turretYaw, self._VehicleGunRotator__gunPitch = self._avatar.vehicle.getServerGunAngles()
            forceValueRefresh = True
    return func(self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh)


@on_event(events.PlayerAvatar.startGUI.after)
def new__startGUI(*args):
    settings = settings_service.getComponentDict(config)
    if settings[GLOBAL.ENABLED] and settings[SERVER_TURRET_SYNC.ACTIVATE_MESSAGE]:
        callback(5.0, lambda: sendPanelMessage(config.i18n['UI_battle_activateMessage']))


def decodeRestrictedValueFromUint(code, bits, minBound, maxBound):
    code -= 0.5
    t = float(code) / ((1 << bits) - 1)
    return minBound + t * (maxBound - minBound)


def decodeAngleFromUint(code, bits):
    code -= 0.5
    return math.pi * 2.0 * code / (1 << bits) - math.pi


gun_rotation_shared.decodeRestrictedValueFromUint = decodeRestrictedValueFromUint
gun_rotation_shared.decodeAngleFromUint = decodeAngleFromUint
