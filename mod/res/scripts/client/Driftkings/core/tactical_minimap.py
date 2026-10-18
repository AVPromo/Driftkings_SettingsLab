# -*- coding: utf-8 -*-
"""Unbound Tactical Minimap prototype policy. No game reads, hooks or listeners.

Production replacement is intentionally unavailable until native input/entry
parity and renderer recovery are verified. Nothing in this module hides Flash.
"""
import math

MODES = ('vanilla', 'driftkings')
THEMES = ('dark', 'military', 'minimal')
CLASSES = ('lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG')
SIDES = ('player', 'ally', 'enemy', 'platoon')
DEFAULTS = {'minimapMode': 'vanilla', 'theme': 'dark', 'size': 320,
            'mapOpacity': 0.85, 'iconScale': 1.0, 'showGrid': True,
            'showVehicleNames': True, 'fontSize': 12}
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
