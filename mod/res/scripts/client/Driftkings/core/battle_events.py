# -*- coding: utf-8 -*-
"""Shared battle notifications. Wrappers preserve the original game calls."""
import logging

from Avatar import PlayerAvatar
from Vehicle import Vehicle
from VehicleGunRotator import VehicleGunRotator
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin

from Driftkings.core.hooks import override
from Driftkings.core.signals import Signal
from Driftkings.core.keyboard import keyboard
from Driftkings.ui import g_events

LOG = logging.getLogger('Driftkings.BattleEvents')


class BattleEvents(object):
    def __init__(self):
        self.healthBefore = Signal()
        self.healthDetailed = Signal()
        self.appearanceDetailed = Signal()
        self.feedback = Signal()
        self.dispersion = Signal()
        self.loaded = Signal()
        self.started = Signal()
        self.ended = Signal()
        self.appeared = Signal()
        self.health = Signal()
        self.visibility = Signal()
        self.killed = Signal()
        self.key = Signal()
        self.owners = set()
        self.arena = None
        self.hooked = False
        self.bound = False

    def acquire(self, owner):
        if owner in self.owners:
            return
        first = not self.owners
        self.owners.add(owner)
        if not first:
            return
        try:
            if not self.hooked:
                override(PlayerAvatar, '_PlayerAvatar__startGUI', self.startGUI)
                override(PlayerAvatar, '_PlayerAvatar__destroyGUI', self.destroyGUI)
                override(PlayerAvatar, 'vehicle_onAppearanceReady', self.appearanceReady)
                override(PlayerAvatar, 'onBattleEvents', self.battleFeedback)
                override(Vehicle, 'onHealthChanged', self.healthChanged)
                override(ArenaVehiclesPlugin, '_setInAoI', self.visibilityChanged)
                override(VehicleGunRotator, 'updateRotationAndGunMarker', self.dispersionChanged)
                self.hooked = True
            g_events.onBattleLoaded += self.onLoaded
            self.bound = True
            keyboard.subscribe(self.onKey)
        except Exception:
            self.release(owner)
            raise

    def release(self, owner):
        if owner not in self.owners:
            return
        self.owners.remove(owner)
        if not self.owners:
            self.detachArena()
            if self.bound:
                g_events.onBattleLoaded -= self.onLoaded
                self.bound = False
            keyboard.unsubscribe(self.onKey)

    def detachArena(self):
        if self.arena is not None:
            self.arena.onVehicleKilled -= self.onKilled
            self.arena = None

    def start(self):
        self.acquire(self)

    def stop(self):
        for owner in tuple(self.owners):
            self.release(owner)
        for name in ('started', 'ended', 'loaded', 'appeared', 'health', 'visibility',
                     'killed', 'key', 'dispersion', 'healthBefore', 'healthDetailed',
                     'appearanceDetailed', 'feedback'):
            getattr(self, name).clear()

    def startGUI(self, original, avatar, *args, **kwargs):
        if not self.owners:
            return original(avatar, *args, **kwargs)
        from Driftkings.common.utils import events
        events.PlayerAvatar.startGUI.before.event(avatar, *args, **kwargs)
        result = original(avatar, *args, **kwargs)
        arena = getattr(avatar, 'arena', None)
        if arena is not self.arena:
            self.detachArena()
            self.arena = arena
            if arena is not None:
                arena.onVehicleKilled += self.onKilled
        self.started.emit()
        events.PlayerAvatar.startGUI.after.event(avatar, *args, **kwargs)
        return result

    def destroyGUI(self, original, avatar, *args, **kwargs):
        if not self.owners:
            return original(avatar, *args, **kwargs)
        from Driftkings.common.utils import events
        events.PlayerAvatar.destroyGUI.before.event(avatar, *args, **kwargs)
        self.ended.emit()
        try:
            result = original(avatar, *args, **kwargs)
        finally:
            self.detachArena()
        events.PlayerAvatar.destroyGUI.after.event(avatar, *args, **kwargs)
        return result

    def appearanceReady(self, original, avatar, vehicle, *args, **kwargs):
        result = original(avatar, vehicle, *args, **kwargs)
        if self.owners:
            self.appeared.emit(vehicle.id)
            self.appearanceDetailed.emit(avatar, vehicle, *args, **kwargs)
        return result

    def healthChanged(self, original, vehicle, health, *args, **kwargs):
        if self.owners:
            self.healthBefore.emit(vehicle, health, *args, **kwargs)
        result = original(vehicle, health, *args, **kwargs)
        if self.owners:
            self.health.emit(vehicle.id, health)
            self.healthDetailed.emit(vehicle, health, *args, **kwargs)
        return result

    def battleFeedback(self, original, avatar, *args, **kwargs):
        result = original(avatar, *args, **kwargs)
        if self.owners:
            self.feedback.emit(avatar, *args, **kwargs)
        return result

    def visibilityChanged(self, original, plugin, entry, visible, *args, **kwargs):
        result = original(plugin, entry, visible, *args, **kwargs)
        if self.owners:
            for vehicleID, candidate in plugin._entries.items():
                if candidate == entry:
                    self.visibility.emit(vehicleID, visible)
                    break
        return result

    def dispersionChanged(self, original, rotator, *args, **kwargs):
        result = original(rotator, *args, **kwargs)
        if self.owners:
            self.dispersion.emit(rotator)
        return result

    def onLoaded(self, *args):
        self.loaded.emit()

    def onKilled(self, targetID, *args):
        self.killed.emit(targetID)

    def onKey(self, event):
        if self.owners:
            self.key.emit(event)


battleEvents = BattleEvents()
