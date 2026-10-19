# -*- coding: utf-8 -*-
"""Unbound read-only native minimap adapter for integration tests.

No event subscriptions, UI changes, pings or BigWorld entity reads. The adapter
is deliberately not installed by the feature loader. Its audit snapshots are
not accepted by the synthetic renderer and do not enable production mode.
"""
import weakref

from Driftkings.core.tactical_minimap import CLASSES, coordinates, finite


class NativeMinimapAdapter(object):
    def __init__(self, component, session, matrix_position, aoi_location, native_size, plugin_type=None, cell_name=None, far_location=2):
        # Native component lifecycle remains owned by Scaleform. Never retain it.
        self._component = weakref.ref(component)
        self._session = weakref.ref(session)
        self._matrix_position = matrix_position
        self._aoi_location = aoi_location
        self._far_location = far_location
        self._native_size = tuple(native_size)
        self._plugin_type = plugin_type
        self._cell_name = cell_name
        self._closed = False

    def close(self):
        self._closed = True
        self._component = self._session = self._matrix_position = self._cell_name = None

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
            get_player_id = getattr(arena_dp, 'getPlayerVehicleID', None)
            player_id = get_player_id() if get_player_id is not None else None
        except Exception:
            result['reason'] = 'native-contract-unavailable'
            return result
        result.update(available=True, bounds=bounds, texture=texture,
                      nativeSize=self._native_size, partial=True,
                      limitations=['alive-published-allies-and-aoi-enemies', 'personal-player-separate',
                                   'no-pings-zones-or-ranges', 'no-orientation'],
                      entryAudit={'total': len(entries), 'unpublished': 0, 'class': 0, 'matrix': 0, 'bounds': 0, 'errors': 0})
        for vehicle_id, entry in entries:
            try:
                # FAR is accepted only for allies still published by the native
                # minimap. Never access a matrix for an enemy outside AoI.
                if not entry.isActive() or not entry.isAlive():
                    result['entryAudit']['unpublished'] += 1
                    continue
                enemy, location = entry.isEnemy(), entry.getLocation()
                allowed = (entry.isInAoI() and location == self._aoi_location or
                           not enemy and location == self._far_location)
                if not allowed:
                    result['entryAudit']['unpublished'] += 1
                    continue
                vehicle_class = entry.getClassTag()
                if vehicle_class not in CLASSES:
                    result['entryAudit']['class'] += 1
                    continue
                provider = entry.getMatrix()
                if provider is None:
                    result['entryAudit']['matrix'] += 1
                    continue
                x, z = self._matrix_position(provider)
                point = coordinates(x, z, bounds)
                if point is None:
                    result['entryAudit']['bounds'] += 1
                    continue
                side = ('enemy' if enemy else 'player' if player_id is not None and vehicle_id == player_id else
                        'platoon' if arena_dp.isSquadMan(vID=vehicle_id) else 'ally')
                info = arena_dp.getVehicleInfo(vehicle_id)
                name = info.getDisplayedName() if info is not None else u''
                native_cell = None
                if self._cell_name is not None:
                    try:
                        native_cell = self._cell_name(x, z, (lower, upper))
                    except Exception:
                        pass  # Cell annotation is optional; keep the published position.
                result['markers'].append({'cell': native_cell, 'id': vehicle_id, 'visible': True, 'state': 'visible',
                                          'vehicleClass': vehicle_class, 'side': side,
                                          'name': name, 'x': point[0], 'y': point[1]})
            except Exception:
                # One expired native entry must not invalidate other entries.
                result['entryAudit']['errors'] += 1
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
    from gui.battle_control.minimap_utils import MINIMAP_SIZE, getCellIdFromPosition, getCellName

    def position(provider):
        value = Math.Matrix(provider).translation
        return value.x, value.z

    def cell_name(x, z, bounds):
        return getCellName(getCellIdFromPosition(Math.Vector3(x, 0, z), bounds, 10), 10)

    return NativeMinimapAdapter(component, session, position, VEHICLE_LOCATION.AOI, MINIMAP_SIZE, type(plugin), cell_name, VEHICLE_LOCATION.FAR)


def owns_player_marker(component):
    """Only the live player's native personal entry, never a spectator/killer."""
    try:
        personal = component.getPlugin('personal')
        allowed = ('gui.Scaleform.daapi.view.battle.shared.minimap.plugins',
                   'Driftkings.battle.minimap_enhancements')
        if personal is None or type(personal).__module__ not in allowed:
            return False
        dp = component.sessionProvider.getArenaDP()
        vehicle_id = dp.getPlayerVehicleID()
        info = dp.getVehicleInfo(vehicle_id)
        return bool(vehicle_id and personal._ctrlVehicleID == vehicle_id and
                    personal._getPlayerVehicleID() == vehicle_id and info is not None and
                    info.isAlive() and not info.isObserver())
    except Exception:
        return False


def native_player_point(component, record):
    """Read the current native personal matrix, never Flash screen coordinates."""
    if not record or not record.get('active') or not owns_player_marker(component):
        return None
    personal = component.getPlugin('personal')
    if personal._getViewPointID() != record.get('id') or record.get('matrix') is None:
        return None
    import Math
    from math import degrees
    from gui.battle_control.minimap_utils import getCellIdFromPosition, getCellName
    matrix = Math.Matrix(record['matrix'])
    position = matrix.translation
    lower, upper = component.getBoundingBox()
    point = coordinates(position.x, position.z, (lower[0], lower[1], upper[0], upper[1]))
    if point is None:
        return None
    yaw = finite(matrix.yaw)
    return {'x': point[0], 'y': point[1], 'heading': degrees(yaw) % 360, 'side': 'player',
            'cell': getCellName(getCellIdFromPosition(position, (lower, upper), 10), 10)}


def native_objective_points(component, records):
    """Positions of currently active bases/control points published via addEntry."""
    import Math
    lower, upper = component.getBoundingBox()
    bounds = (lower[0], lower[1], upper[0], upper[1])
    result = []
    for record in list(records.values())[:16]:
        if not record.get('active') or record.get('matrix') is None:
            continue
        try:
            position = Math.Matrix(record['matrix']).translation
            point = coordinates(position.x, position.z, bounds)
            if point is not None:
                result.append({'kind': record['kind'], 'x': point[0], 'y': point[1]})
        except Exception:
            continue
    return result
