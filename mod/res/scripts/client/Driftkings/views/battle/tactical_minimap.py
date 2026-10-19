# -*- coding: utf-8 -*-
"""Unbound read-only native minimap adapter for integration tests.

No event subscriptions, UI changes, pings or BigWorld entity reads. The adapter
is deliberately not installed by the feature loader. Its audit snapshots are
not accepted by the synthetic renderer and do not enable production mode.
"""
import weakref

from Driftkings.core.tactical_minimap import CLASSES, coordinates, finite


class NativeMinimapAdapter(object):
    def __init__(self, component, session, matrix_position, aoi_location, native_size, plugin_type=None):
        # Native component lifecycle remains owned by Scaleform. Never retain it.
        self._component = weakref.ref(component)
        self._session = weakref.ref(session)
        self._matrix_position = matrix_position
        self._aoi_location = aoi_location
        self._native_size = tuple(native_size)
        self._plugin_type = plugin_type
        self._closed = False

    def close(self):
        self._closed = True
        self._component = self._session = self._matrix_position = None

    def capture(self):
        result = {'source': 'native-minimap-audit', 'available': False,
                  'nativePresentationChanged': False, 'lostContactAvailable': False, 'markers': []}
        if self._closed:
            result['reason'] = 'adapter-closed'
            return result
        component, session = self._component(), self._session()
        if component is None or session is None:
            result['reason'] = 'native-owner-unavailable'
            return result
        try:
            arena = session.arenaVisitor.type
            lower, upper = component.getBoundingBox()
            bounds = tuple(finite(value) for value in (lower[0], lower[1], upper[0], upper[1]))
            coordinates(bounds[0], bounds[1], bounds)
            texture = arena.getMinimapTexture()
            if not texture or not isinstance(texture, (str, type(u''))):
                raise ValueError('Missing native minimap texture')
            plugin = component.getPlugin('vehicles')
            if plugin is None or (self._plugin_type is not None and type(plugin) is not self._plugin_type):
                raise ValueError('Native vehicle plugin owner changed')
            if not isinstance(plugin._entries, dict):
                raise ValueError('Missing native vehicle entries')
            arena_dp = session.getArenaDP()
            if arena_dp is None:
                raise ValueError('Missing native arena data provider')
            entries = list(plugin._entries.items())
        except Exception:
            result['reason'] = 'native-contract-unavailable'
            return result
        result.update(available=True, bounds=bounds, texture=texture,
                      nativeSize=self._native_size, partial=True,
                      limitations=['aoi-alive-vehicles-only', 'no-player-camera-entry',
                                   'no-pings-zones-or-ranges', 'no-orientation'])
        for vehicle_id, entry in entries:
            try:
                # Check native publication state BEFORE accessing any matrix.
                # AOI_TO_FAR is a transitional copied position; never publish it.
                if (not entry.isActive() or not entry.isAlive() or not entry.isInAoI() or
                        entry.getLocation() != self._aoi_location):
                    continue
                vehicle_class = entry.getClassTag()
                if vehicle_class not in CLASSES:
                    continue
                provider = entry.getMatrix()
                if provider is None:
                    continue
                x, z = self._matrix_position(provider)
                point = coordinates(x, z, bounds)
                if point is None:
                    continue
                enemy = entry.isEnemy()
                side = 'enemy' if enemy else 'platoon' if arena_dp.isSquadMan(vID=vehicle_id) else 'ally'
                info = arena_dp.getVehicleInfo(vehicle_id)
                name = info.getDisplayedName() if info is not None else u''
                result['markers'].append({'id': vehicle_id, 'visible': True, 'state': 'visible',
                                          'vehicleClass': vehicle_class, 'side': side,
                                          'name': name, 'x': point[0], 'y': point[1]})
            except Exception:
                # One expired native entry must not invalidate other entries.
                continue
        return result


def native_adapter(component, session):
    """Factory using contracts verified in the local 2.4.1 SRC, called explicitly.

    Not registered in getBattleViews(), not hooked, and not a production mode.
    """
    plugin = component.getPlugin('vehicles')
    allowed = ('gui.Scaleform.daapi.view.battle.shared.minimap.plugins',
               'Driftkings.battle.minimap_enhancements')
    if plugin is None or type(plugin).__module__ not in allowed:
        raise ValueError('Unverified third-party or mode-specific minimap plugin')
    from Driftkings.common import xvmInstalled
    if xvmInstalled:
        raise ValueError('XVM owns the minimap; the audit adapter is unavailable')
    import Math
    from gui.battle_control.battle_constants import VEHICLE_LOCATION
    from gui.battle_control.minimap_utils import MINIMAP_SIZE

    def position(provider):
        value = Math.Matrix(provider).translation
        return value.x, value.z

    return NativeMinimapAdapter(component, session, position, VEHICLE_LOCATION.AOI, MINIMAP_SIZE, type(plugin))
