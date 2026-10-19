# -*- coding: utf-8 -*-
"""Small diagnostic transport contract. Publishes bounded current allied samples without identities or enemy positions."""
import re

from Driftkings.core.tactical_minimap import CLASSES, finite

PROTOCOL = 1


def payload(enabled, acknowledged, snapshot=None, generation=0, graphics=None, calibration=None):
    data = {'enabled': bool(enabled), 'protocol': PROTOCOL, 'generation': generation, 'effectiveMode': 'vanilla',
            'acknowledged': bool(acknowledged), 'nativePresentationChanged': False,
            'available': False, 'partial': True, 'markerCount': 0,
            'reason': 'waiting-native', 'lostContactAvailable': False, 'allyStatus': 'waiting-native'}
    if not enabled:
        data['allyStatus'] = 'disabled'
        data['reason'] = 'disabled'
        return data
    if calibration is not None:
        data['calibration'] = calibration_result(calibration)
    if graphics is not None:
        result = graphics_result(graphics)
        if result is not None:
            data['graphics'] = result
    if not snapshot:
        return data
    data['reason'] = snapshot.get('reason', 'native-contract-unavailable')
    if snapshot.get('source') != 'native-minimap-audit' or snapshot.get('available') is not True:
        return data
    try:
        bounds = [finite(value) for value in snapshot['bounds']]
        size = [finite(value) for value in snapshot['nativeSize']]
        texture = snapshot['texture']
        if (len(bounds) != 4 or bounds[2] <= bounds[0] or bounds[3] <= bounds[1] or
                len(size) != 2 or min(size) <= 0 or not isinstance(texture, (str, type(u'')))):
            raise ValueError('Invalid probe metadata')
        count = len(snapshot.get('markers', []))
    except (KeyError, ValueError, TypeError, OverflowError):
        data['reason'] = 'invalid-native-metadata'
        return data
    data['allyStatus'] = ('waiting-handshake' if not acknowledged else
                          'waiting-geometry' if not data.get('calibration', {}).get('available') else
                          'no-current-ally')
    if acknowledged and data.get('calibration', {}).get('available') is True:
        points = allied_calibration_points(snapshot.get('markers', []))
        data['alliedPoints'] = points
        point = points[0] if points else None
        if point is not None:
            data['alliedPoint'] = point
            data['allyStatus'] = 'ready'
    uri = texture_uri(texture)
    if uri is not None:
        data['textureUri'] = uri
    else:
        data['cartographyReason'] = 'unsupported-texture-path'
    data.update(available=True, bounds=bounds, nativeSize=size, texture=texture[:256],
                markerCount=count, reason='ready' if acknowledged else 'waiting-handshake')
    return data


def accepts_ack(args, generation):
    return (isinstance(args, dict) and not isinstance(args.get('protocol'), bool) and
            isinstance(args.get('protocol'), (int, float)) and
            args['protocol'] == PROTOCOL and not isinstance(args.get('generation'), bool) and
            isinstance(args.get('generation'), (int, float)) and args['generation'] == generation)


def graphics_result(args):
    """A DOM capability report is not evidence of painted SVG or production parity."""
    if not isinstance(args, dict) or type(args.get('svgApi')) is not bool:
        return None
    count = args.get('glyphCount')
    if isinstance(count, bool) or not isinstance(count, (int, float)):
        return None
    if not 0 <= count <= 21 or int(count) != count:
        return None
    if args['svgApi'] and count != 21:
        return None
    return {'svgApi': args['svgApi'], 'glyphCount': int(count)}


def texture_uri(path):
    """Only bounded virtual map resources; no filesystem, network or CSS fragments."""
    if not isinstance(path, (str, type(u''))) or len(path) > 256:
        return None
    if path.startswith('img://'):
        path = path[6:]
    if not re.match(r'^(?:spaces/[A-Za-z0-9_/-]+\.(?:dds|png)|gui/maps/icons/map/[A-Za-z0-9_-]+\.png)\Z', path):
        return None
    if any(part in ('', '.', '..') for part in path.split('/')):
        return None
    return 'img://' + path


def calibration_result(data):
    """UI background rectangle only; not a vehicle coordinate or an input route."""
    unavailable = {'available': False, 'reason': 'invalid-geometry'}
    if not isinstance(data, dict):
        return unavailable
    if data.get('available') is False:
        reason = data.get('reason')
        allowed = ('minimap-unavailable', 'background-unavailable', 'stage-unavailable', 'empty-background', 'map-area-unavailable', 'empty-map-area', 'native-geometry-unavailable')
        return {'available': False, 'reason': reason if reason in allowed else 'unavailable'}
    if data.get('available') is not True:
        return unavailable
    try:
        values = dict((key, finite(data[key])) for key in
                      ('x', 'y', 'width', 'height', 'stageWidth', 'stageHeight'))
        width, height = values['stageWidth'], values['stageHeight']
        if not (0 < width <= 32768 and 0 < height <= 32768 and
                0 < values['width'] <= 4 * width and 0 < values['height'] <= 4 * height and
                -4 * width <= values['x'] <= 4 * width and -4 * height <= values['y'] <= 4 * height):
            return unavailable
    except (KeyError, TypeError, ValueError, OverflowError):
        return unavailable
    return dict(values, available=True, normalized={
        'x': values['x'] / width, 'y': values['y'] / height,
        'width': values['width'] / width, 'height': values['height'] / height})


def allied_calibration_point(markers):
    """One currently published ally only; no identity, history or enemy coordinates."""
    if not isinstance(markers, list):
        return None
    for marker in markers[:64]:
        if (not isinstance(marker, dict) or marker.get('visible') is not True or
                marker.get('state') != 'visible' or marker.get('side') not in ('ally', 'platoon')):
            continue
        try:
            x, y = finite(marker['x']), finite(marker['y'])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if 0 <= x <= 1 and 0 <= y <= 1:
            point = {'x': x, 'y': y}
            if marker.get('vehicleClass') in CLASSES:
                point['vehicleClass'] = marker['vehicleClass']
                point['side'] = marker['side']
            cell = marker.get('cell')
            if isinstance(cell, (str, type(u''))) and re.match(r'^[A-HJK][1-90]\Z', cell):
                point['cell'] = cell
            return point
    return None


def geometry_response(value):
    """Primitive-string Flash return avoids relying on GFx object conversion."""
    if not isinstance(value, (str, type(u''))) or len(value) > 256:
        return calibration_result(None)
    parts = value.split('|')
    if len(parts) == 2 and parts[0] == '0':
        return calibration_result({'available': False, 'reason': parts[1]})
    if len(parts) != 7 or parts[0] != '1':
        return calibration_result(None)
    data = dict(zip(('x', 'y', 'width', 'height', 'stageWidth', 'stageHeight'), parts[1:]))
    data['available'] = True
    return calibration_result(data)


def allied_calibration_points(markers):
    """Bounded current-frame slots; no native IDs or position history retained."""
    if not isinstance(markers, list):
        return []
    result = []
    for marker in markers[:64]:
        point = allied_calibration_point([marker])
        if point is not None:
            result.append(point)
    return result
