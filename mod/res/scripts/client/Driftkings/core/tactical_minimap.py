# -*- coding: utf-8 -*-
"""Unbound Tactical Minimap prototype policy. No game reads, hooks or listeners.

Production replacement is intentionally unavailable until native input/entry
parity and renderer recovery are verified. Nothing in this module hides Flash.
"""
import math
import re

MODES = ('vanilla', 'driftkings')
THEMES = ('dark', 'military', 'minimal')
CLASSES = ('lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG')
SIDES = ('player', 'ally', 'enemy', 'platoon')
DEFAULTS = {'minimapMode': 'vanilla', 'theme': 'dark', 'size': 320,
            'mapOpacity': 0.85, 'iconScale': 1.0, 'showGrid': True,
            'showVehicleNames': True, 'fontSize': 12, 'followNativeSize': True,
            'allyColor': '#67cf69', 'enemyColor': '#ee6868', 'platoonColor': '#ffc45b'}
# This is a release gate, not a user setting. Tests must never imply it is enabled.
PRODUCTION_REPLACEMENT_VERIFIED = False
LOST_CONTACT_VERIFIED = False


def finite(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a coordinate')
    try:
        value = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError('Invalid numeric value')
    if math.isnan(value) or math.isinf(value):
        raise ValueError('Non-finite numeric value')
    return value


def preferences(values=None):
    """Validate optional visual overrides without mutating stored configuration."""
    if values is None:
        values = {}
    if not isinstance(values, dict):
        raise ValueError('Invalid tactical preferences')
    result = dict((key, value) for key, value in DEFAULTS.items() if key != 'minimapMode')
    for key in result:
        if key in values:
            result[key] = values[key]
    if result['theme'] not in THEMES:
        raise ValueError('Unknown tactical theme')
    for key in ('followNativeSize', 'showGrid', 'showVehicleNames'):
        if type(result[key]) is not bool:
            raise ValueError('Invalid tactical switch: ' + key)
    for key, low, high in (('size', 160, 640), ('fontSize', 8, 24),
                           ('mapOpacity', 0, 1), ('iconScale', .5, 3)):
        value = result[key]
        if type(value) not in (int, float) or not low <= finite(value) <= high:
            raise ValueError('Invalid tactical number: ' + key)
        if key in ('size', 'fontSize') and value != int(value):
            raise ValueError('Expected tactical integer: ' + key)
    for key in ('allyColor', 'enemyColor', 'platoonColor'):
        value = result[key]
        if not isinstance(value, (str, type(u''))) or not re.match(r'^#[0-9a-fA-F]{6}\Z', value):
            raise ValueError('Invalid tactical color: ' + key)
    return result


def validate_settings(data):
    if data.get('minimapMode', 'vanilla') not in MODES:
        raise ValueError('Unknown minimap mode')
    preferences(data.get('tactical'))


def coordinates(x, z, bounds):
    """x/z -> normalized top-left map coordinates; reject out-of-map entries.

    North is +z in this preview convention; real native map orientation still
    needs verification. Rectangular and offset bounding boxes are supported.
    """
    left, bottom, right, top = [finite(value) for value in bounds]
    if right <= left or top <= bottom:
        raise ValueError('Invalid arena bounds')
    x, z = finite(x), finite(z)
    if not left <= x <= right or not bottom <= z <= top:
        return None
    return ((x - left) / (right - left), (top - z) / (top - bottom))


def heading(dx, dz):
    """Preview heading: north=0, east=90. Never derive unseen vehicle headings."""
    dx, dz = finite(dx), finite(dz)
    if dx == 0 and dz == 0:
        return None
    return math.degrees(math.atan2(dx, dz)) % 360


def selection(preference='vanilla', conflict=False, renderer_ready=False):
    """Preserve requested preference, but always leave native UI in control."""
    if preference not in MODES:
        raise ValueError('Unknown minimap mode')
    reason = None
    if preference == 'driftkings':
        reason = ('third-party-conflict' if conflict else
                  'renderer-unavailable' if not renderer_ready else 'native-parity-unverified')
    return {'requestedMode': preference, 'effectiveMode': 'vanilla',
            'nativeVisible': True, 'rendererVisible': False, 'reason': reason,
            'lostContactAvailable': False}


def preview_snapshot(markers, bounds, source='synthetic-preview'):
    """Stateless synthetic fixture adapter, deliberately not a battle adapter.

    Reject invisible/lost enemy entries before processing their coordinates.
    No cached last positions, BigWorld entity access or location inference.
    """
    if source != 'synthetic-preview':
        raise ValueError('No verified battle data adapter is installed')
    coordinates(bounds[0], bounds[1], bounds)
    result, seen = [], set()
    for marker in markers:
        if marker.get('visible') is not True or marker.get('state') not in ('visible', 'destroyed'):
            continue
        side, vehicle_class = marker.get('side'), marker.get('vehicleClass')
        if side not in SIDES or vehicle_class not in CLASSES:
            raise ValueError('Unknown vehicle semantics')
        identifier = marker['id']
        if isinstance(identifier, bool) or not isinstance(identifier, int) or identifier < 0 or identifier in seen:
            raise ValueError('Invalid or duplicate marker id')
        seen.add(identifier)
        point = coordinates(marker['x'], marker['z'], bounds)
        if point is None:
            continue
        name = marker.get('name', '')
        if not isinstance(name, type(u'')):
            name = name.decode('utf-8') if isinstance(name, bytes) else u''
        value = {'id': identifier, 'visible': True, 'x': point[0], 'y': point[1], 'side': side,
                 'vehicleClass': vehicle_class, 'state': marker['state'], 'name': name[:64]}
        if 'direction' in marker and marker['state'] != 'destroyed':
            value['heading'] = heading(*marker['direction'])
        result.append(value)
    return {'source': source, 'markers': result, 'lostContactAvailable': False}


def native_click_point(x, y, native_size):
    """Normalized point -> native local pixels, not world metres.

    ClassicMinimapPingPlugin._getClickPosition delegates to
    minimap_utils.makePointMatrixByLocal using MINIMAP_SIZE. The caller must
    supply that native constant; the visual size/zoom must not be used here.
    This function never sends a ping or invokes the game component.
    """
    x, y = finite(x), finite(y)
    width, height = [finite(value) for value in native_size]
    if width <= 0 or height <= 0 or not 0 <= x <= 1 or not 0 <= y <= 1:
        raise ValueError('Invalid native click geometry')
    return x * width, y * height


def world_point(x, y, bounds):
    """Inverse of coordinates(), following native x/right, z/north mapping."""
    x, y = finite(x), finite(y)
    left, bottom, right, top = [finite(value) for value in bounds]
    if right <= left or top <= bottom or not 0 <= x <= 1 or not 0 <= y <= 1:
        raise ValueError('Invalid map point')
    return left + x * (right - left), top - y * (top - bottom)
