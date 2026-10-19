# -*- coding: utf-8 -*-
"""Native minimap reads and guarded explicit position-input delegation.

The adapter does not subscribe to events, query world entities or retain past
positions. Its snapshots feed diagnostics, not production replacement. Input
delegation calls the stock classic handler only for validated user clicks.
"""
import weakref

from Driftkings.core.tactical_minimap import CLASSES, coordinates, finite


class NativeMinimapAdapter(object):
    def __init__(self, component, session, matrix_position, aoi_location, native_size, plugin_type=None, cell_name=None, far_location=2, topography=False):
        # Native component lifecycle remains owned by Scaleform. Never retain it.
        self._component = weakref.ref(component)
        self._session = weakref.ref(session)
        self._matrix_position = matrix_position
        self._aoi_location = aoi_location
        self._far_location = far_location
        self._native_size = tuple(native_size)
        self._plugin_type = plugin_type
        self._cell_name = cell_name
        self._topography = topography
        self._closed = False

    def close(self):
        self._closed = True
        self._component = self._session = self._matrix_position = self._cell_name = None

    def capture(self):
        result = {'source': 'native-minimap-audit', 'available': False,
                  'nativePresentationChanged': False, 'lostContactAvailable': False, 'markers': [], 'destroyedMarkers': [], 'trainingMarkers': []}
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
            if self._topography and not _topography_context(component, session, plugin):
                raise ValueError('Topography context changed')
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
                      context='topography' if self._topography else 'classic',
                      nativeSize=self._native_size, partial=True,
                      limitations=['alive-published-allies-and-aoi-enemies', 'personal-player-separate',
                                   'no-pings-zones-or-ranges', 'no-orientation'],
                      entryAudit={'total': len(entries), 'unpublished': 0, 'class': 0, 'matrix': 0, 'bounds': 0, 'errors': 0})
        for vehicle_id, entry in entries:
            try:
                # FAR also carries currently spotted distant enemies. Native
                # isInAoI stays true for those publications; hidden entries are
                # reset to UNDEFINED/false by _hideVehicle before any read here.
                if not entry.isActive():
                    result['entryAudit']['unpublished'] += 1
                    continue
                enemy, location = entry.isEnemy(), entry.getLocation()
                alive = entry.isAlive()
                # Topography's active static hints are intentionally visible
                # even before a bot is spotted. Keep them in a separate channel.
                allowed = (self._topography or entry.isInAoI() and location in (self._aoi_location, self._far_location) or
                           alive and not enemy and location == self._far_location)
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
                lookup_id = entry.getOwnVehicleID() if self._topography else vehicle_id
                side = ('training' if self._topography else 'enemy' if enemy else 'player' if player_id is not None and vehicle_id == player_id else
                        'platoon' if arena_dp.isSquadMan(vID=vehicle_id) else 'ally')
                info = arena_dp.getVehicleInfo(lookup_id)
                name = info.getDisplayedName() if info is not None else u''
                native_cell = None
                if self._cell_name is not None:
                    try:
                        native_cell = self._cell_name(x, z, (lower, upper))
                    except Exception:
                        pass  # Cell annotation is optional; keep the published position.
                bucket = 'trainingMarkers' if self._topography else 'markers' if alive else 'destroyedMarkers'
                row = {'cell': native_cell, 'id': vehicle_id, 'visible': True,
                                          'state': 'destroyed' if not alive else 'training' if self._topography else 'visible',
                                          'vehicleClass': vehicle_class, 'side': side,
                                          'name': name, 'vehicleLabel': name, 'x': point[0], 'y': point[1]}
                if self._topography:
                    row['goal'] = bool(entry.isGoalForPlayer())
                result[bucket].append(row)
            except Exception:
                # One expired native entry must not invalidate other entries.
                result['entryAudit']['errors'] += 1
                continue
        return result


def _topography_context(component, session, plugin):
    native_module = 'gui.Scaleform.daapi.view.battle.maps_training.minimap'
    if (type(plugin).__module__ != native_module or type(plugin).__name__ != 'BotAppearNotificationPlugin' or
            type(component).__module__ != native_module or type(component).__name__ != 'MapsTrainingMinimapComponent'):
        return False
    from constants import ARENA_GUI_TYPE
    return session.arenaVisitor.gui.guiType == ARENA_GUI_TYPE.MAPS_TRAINING


def native_surface_audit(component):
    """Read the exact C++ surface created by MinimapComponent; never mutate it.

    The private field name is audited against the local 2.4.1 SRC. Unknown
    engine types are rejected before any rendering properties are inspected.
    """
    surface = getattr(component, '_MinimapComponent__component', None)
    if surface is None:
        return {'available': False, 'reason': 'native-surface-unavailable'}
    if (type(surface).__module__, type(surface).__name__) != ('GUI', 'WGMinimapFlashAS3'):
        return {'available': False, 'reason': 'unsupported-native-surface'}
    result = dict(available=True, className='GUI.WGMinimapFlashAS3', visible=None,
                  colour=None, size=None, inputMode=None, missing=[])
    try:
        value = surface.visible
        if type(value) is not bool:
            raise ValueError('Invalid visibility')
        result['visible'] = value
    except Exception:
        result['missing'].append('visible')
    try:
        value = surface.colour
        colour = [finite(getattr(value, name)) for name in ('x', 'y', 'z', 'w')]
        if not all(0 <= channel <= 255 for channel in colour):
            raise ValueError('Invalid colour channels')
        result['colour'] = colour
    except Exception:
        result['missing'].append('colour')
    try:
        size = [finite(surface.width), finite(surface.height)]
        if not all(0 <= dimension <= 1000000 for dimension in size):
            raise ValueError('Invalid surface dimensions')
        result['size'] = size
    except Exception:
        result['missing'].append('size')
    try:
        value = surface.wg_inputKeyMode
        if type(value) is not int or not 0 <= value <= 32:
            raise ValueError('Invalid input mode')
        result['inputMode'] = value
    except Exception:
        result['missing'].append('inputMode')
    return result


def native_surface_trial_allowed(component):
    try:
        from Driftkings.common import xvmInstalled
        return bool(not xvmInstalled and not component.isModalViewShown() and
                    _topography_context(component, component.sessionProvider, component.getPlugin('vehicles')) and
                    owns_player_marker(component))
    except Exception:
        return False


class NativeSurfaceTrial(object):
    """Two-second training experiment; recovery callback is armed before hiding."""
    def __init__(self, component, schedule, cancel, reporter):
        self.surface = getattr(component, '_MinimapComponent__component', None)
        self.schedule, self.cancel, self.reporter = schedule, cancel, reporter
        self.token = None
        self.status = 'idle'
        self.original = None

    def _status(self, value):
        if value == self.status:
            return
        self.status = value
        try:
            self.reporter(value)
        except Exception:
            pass

    def start(self):
        if self.status != 'idle':
            return self.status
        surface = self.surface
        if surface is None or (type(surface).__module__, type(surface).__name__) != ('GUI', 'WGMinimapFlashAS3'):
            self._status('unsupported-surface')
            return self.status
        try:
            self.original = surface.visible
            if self.original is not True:
                self._status('already-hidden')
                return self.status
            self._status('armed')
            token = self.schedule(2.0, self.expire)
            if token is None:
                raise ValueError('Restoration callback was not armed')
            if self.status != 'armed':
                # A scheduler invoking inline must never result in late hiding.
                self.cancel(token)
                return self.status
            self.token = token
            surface.visible = False
            if surface.visible is not False:
                raise ValueError('Native visibility write was not confirmed')
            self._status('active')
        except Exception:
            if self.status == 'idle':
                self._status('unavailable')
            self.restore()
            if self.status == 'restored':
                self._status('failed-restored')
        return self.status

    def expire(self):
        self.token = None
        self.restore()

    def restore(self):
        if self.status not in ('armed', 'active', 'restore-failed'):
            return self.status
        try:
            if self.surface.visible is not self.original:
                self.surface.visible = self.original
            if self.surface.visible is not self.original:
                raise ValueError('Native restoration was not confirmed')
        except Exception:
            # Keep an already armed expiry if an early restoration failed.
            self._status('restore-failed')
            return self.status
        if self.token is not None:
            token, self.token = self.token, None
            try:
                self.cancel(token)
            except Exception:
                pass
        self.surface = None
        self._status('restored')
        return self.status


def native_adapter(component, session):
    """Factory using contracts verified in the local 2.4.1 SRC, called explicitly.

    Not registered in getBattleViews(), not hooked, and not a production mode.
    """
    plugin = component.getPlugin('vehicles')
    allowed = ('gui.Scaleform.daapi.view.battle.shared.minimap.plugins',
               'Driftkings.battle.minimap_enhancements')
    topography = plugin is not None and _topography_context(component, session, plugin)
    if plugin is None or not topography and type(plugin).__module__ not in allowed:
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

    return NativeMinimapAdapter(component, session, position, VEHICLE_LOCATION.AOI, MINIMAP_SIZE, type(plugin), cell_name, VEHICLE_LOCATION.FAR, topography)


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
        # Native control IDs are 0 at startup and may be None in own-camera
        # updates (observed entering sniper). None is accepted only in native
        # arcade/sniper or strategic modes, with live own identity checked below.
        controlled = personal._ctrlVehicleID
        unassigned_own = (controlled in (0, None) and not personal._isInPostmortemMode() and
                          not personal._isInVideoMode() and not personal._isInFreeCamMode() and
                          (controlled == 0 or personal._isInArcadeMode() or personal._isInStrategicMode()))
        return bool(vehicle_id and (controlled == vehicle_id or unassigned_own) and
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


def native_camera_line(component, record):
    """Only the active arcade direction entry owned by the live player."""
    if not record or not record.get('active') or not record.get('direction') or not owns_player_marker(component):
        return None
    personal = component.getPlugin('personal')
    if (personal._getCameraIDs().get('ArcadeCameraEntry') != record.get('id') or
            personal._getSelectedCameraID() != record.get('id') or record.get('matrix') is None):
        return None
    import Math
    matrix = Math.Matrix(record['matrix'])
    position = matrix.translation
    lower, upper = component.getBoundingBox()
    bounds = tuple(finite(value) for value in (lower[0], lower[1], upper[0], upper[1]))
    point = coordinates(position.x, position.z, bounds)
    if point is None:
        return None
    return _world_direction_line(point, finite(matrix.yaw), bounds)


def _world_direction_line(point, yaw, bounds):
    from math import sin, cos
    dx, dy = sin(yaw) / (bounds[2] - bounds[0]), -cos(yaw) / (bounds[3] - bounds[1])
    distances = []
    for origin, direction in ((point[0], dx), (point[1], dy)):
        if abs(direction) > 1e-12:
            distances.append(((1 if direction > 0 else 0) - origin) / direction)
    if not distances:
        return None
    distance = min(distances)
    return {'x': point[0], 'y': point[1], 'x2': max(0, min(1, point[0] + distance * dx)),
            'y2': max(0, min(1, point[1] + distance * dy))}


def native_position_input_status(component):
    """Conservative capability check for the stock classic position handler."""
    try:
        import BattleReplay
        from Driftkings.common import xvmInstalled
        if BattleReplay.g_replayCtrl.isPlaying:
            return 'diagnostic-replay'
        if xvmInstalled:
            return 'third-party-owner'
        if component.getMinimapDimensions() != 10:
            return 'unsupported-mode'
        plugin = component.getPlugin('pinging')
        if plugin is None:
            return 'native-input-unavailable'
        if (type(plugin).__module__ != 'gui.Scaleform.daapi.view.battle.classic.minimap' or
                type(plugin).__name__ != 'ClassicMinimapPingPlugin'):
            return 'third-party-owner'
        if component.isModalViewShown():
            return 'modal-view'
        return 'ready'
    except Exception:
        return 'native-input-unavailable'


def forward_native_position_input(component, value):
    """One explicit left/right click, delegated once; never retry or send chat here."""
    if isinstance(value, dict) and value.get('target', 'position') != 'position':
        return 'diagnostic-vehicle' if value.get('target') == 'vehicle' else 'invalid-input'
    status = native_position_input_status(component)
    if status != 'ready':
        return status
    try:
        from Driftkings.core.tactical_minimap_probe import input_sample
        from Driftkings.core.tactical_minimap import native_click_point
        from gui.battle_control.minimap_utils import MINIMAP_SIZE
        value = input_sample(value)
        if value is None:
            return 'invalid-input'
        if value['button'] not in (0, 1):
            return 'diagnostic-button'
        x, y = native_click_point(value['x'], value['y'], MINIMAP_SIZE)
        component.onMinimapClicked(x, y, value['button'], value['sizeIndex'])
        return 'forwarded'
    except Exception:
        return 'failed'


def native_strategic_point(component, record):
    """Aim-matrix translation already published for the strategic camera."""
    if not record or not record.get('active') or not owns_player_marker(component):
        return None
    personal = component.getPlugin('personal')
    if (personal._getCameraIDs().get('StrategicCameraEntry') != record.get('id') or
            personal._getSelectedCameraID() != record.get('id') or record.get('matrix') is None or
            not (personal._isInStrategicMode() or personal._isInArtyMode())):
        return None
    import Math
    position = Math.Matrix(record['matrix']).translation
    lower, upper = component.getBoundingBox()
    point = coordinates(position.x, position.z, (lower[0], lower[1], upper[0], upper[1]))
    return {'x': point[0], 'y': point[1]} if point is not None else None


def native_yaw_lines(component, record):
    """Hull-relative limits explicitly enabled on the native personal entry."""
    if not record or not record.get('active') or not record.get('yawLimits') or not owns_player_marker(component):
        return []
    if component.getPlugin('personal')._getViewPointID() != record.get('id') or record.get('matrix') is None:
        return []
    import Math
    from math import radians
    matrix = Math.Matrix(record['matrix'])
    position = matrix.translation
    lower, upper = component.getBoundingBox()
    bounds = tuple(finite(value) for value in (lower[0], lower[1], upper[0], upper[1]))
    point = coordinates(position.x, position.z, bounds)
    if point is None:
        return []
    yaw = finite(matrix.yaw)
    return [_world_direction_line(point, yaw + radians(offset), bounds) for offset in record['yawLimits']]


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
                item = {'kind': record['kind'], 'x': point[0], 'y': point[1]}
                if 'number' in record:
                    item['number'] = record['number']
                    item.update(native_objective_capture(component, record, position))
                result.append(item)
        except Exception:
            continue
    return result


def native_objective_capture(component, record, position):
    """Read the classic controller's current publication; never extrapolate."""
    unknown = {'state': 'unknown'}
    try:
        session = component.sessionProvider
        controller = session.shared.teamBases
        if type(controller).__module__ != 'gui.battle_control.controllers.team_bases_ctrl':
            return unknown
        from gui.battle_control.controllers.team_bases_ctrl import makeClientTeamBaseID, _AVAILABLE_TEAMS_NUMBERS
        number = record['number']
        if record['kind'] == 'controlPoint':
            teams = _AVAILABLE_TEAMS_NUMBERS
        else:
            own_team = session.getArenaDP().getNumberOfTeam()
            teams = []
            for team, location, native_number in session.arenaVisitor.type.getTeamBasePositionsIterator():
                matches_side = (team == own_team) == (record['kind'] == 'allyBase')
                if (matches_side and native_number == number and abs(location[0] - position.x) < .01 and
                        abs(location[2] - position.z) < .01):
                    teams.append(team)
        if not teams:
            return unknown
        states = []
        for team in teams:
            client_id = makeClientTeamBaseID(team, number)
            if controller.isTeamBaseCaptured(client_id):
                states.append({'state': 'captured', 'progress': 100})
                continue
            try:
                points, _, invaders, stopped = controller._getPoints(client_id)
            except KeyError:
                states.append({'state': 'idle', 'progress': 0})
                continue
            points = finite(points)
            if not 0 <= points <= 100:
                continue
            state = 'blocked' if stopped and invaders > 0 else 'capturing' if points > 0 and not stopped else 'idle'
            states.append({'state': state, 'progress': points})
        priority = {'idle': 0, 'capturing': 1, 'blocked': 2, 'captured': 3}
        return max(states, key=lambda value: priority[value['state']]) if states else unknown
    except Exception:
        return unknown


def native_circle_points(component, record):
    if not record or not record.get('active') or record.get('matrix') is None:
        return []
    import Math
    lower, upper = component.getBoundingBox()
    bounds = tuple(finite(value) for value in (lower[0], lower[1], upper[0], upper[1]))
    position = Math.Matrix(record['matrix']).translation
    center = coordinates(position.x, position.z, bounds)
    if center is None:
        return []
    return [dict(value, kind=kind, x=center[0], y=center[1],
                 rx=value['radius'] / (bounds[2] - bounds[0]), ry=value['radius'] / (bounds[3] - bounds[1]))
            for kind, value in record['circles'].items()]


def native_ping_points(component, records):
    """Read currently published communication entries; native deletion owns expiry."""
    import Math
    lower, upper = component.getBoundingBox()
    bounds = (lower[0], lower[1], upper[0], upper[1])
    result = []
    for record in list(records.values())[:32]:
        if not record.get('active') or record.get('matrix') is None:
            continue
        try:
            position = Math.Matrix(record['matrix']).translation
            point = coordinates(position.x, position.z, bounds)
            if point is not None:
                result.append({'x': point[0], 'y': point[1], 'kind': record['kind'], 'state': record['state']})
        except Exception:
            continue
    return result
