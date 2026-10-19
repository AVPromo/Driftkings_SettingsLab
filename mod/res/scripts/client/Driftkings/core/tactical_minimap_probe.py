# -*- coding: utf-8 -*-
"""Small diagnostic transport contract. Publishes bounded current allied samples without identities or enemy positions."""
import re

from Driftkings.core.tactical_minimap import CLASSES, finite

PROTOCOL = 1
OBJECTIVE_SYMBOLS = {'AllyTeamBaseEntry': 'allyBase', 'EnemyTeamBaseEntry': 'enemyBase',
                     'ControlPointEntry': 'controlPoint'}


def payload(enabled, acknowledged, snapshot=None, generation=0, graphics=None, calibration=None):
    data = {'enabled': bool(enabled), 'protocol': PROTOCOL, 'generation': generation, 'effectiveMode': 'vanilla',
            'acknowledged': bool(acknowledged), 'nativePresentationChanged': False,
            'available': False, 'partial': True, 'markerCount': 0,
            'reason': 'waiting-native', 'lostContactAvailable': False, 'allyStatus': 'waiting-native', 'playerAvailable': False}
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
        player = player_point((calibration or {}).get('player'))
        if player is not None:
            points = [player] + [point for point in points if point.get('side') != 'player']
        data['playerAvailable'] = any(point.get('side') == 'player' for point in points)
        data['objectives'] = objective_points(snapshot.get('objectives', []))
        data['circles'] = circle_points(snapshot.get('circles', []))
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
                marker.get('state') != 'visible' or marker.get('side') not in ('player', 'ally', 'platoon')):
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


def player_point(value):
    if not isinstance(value, dict):
        return None
    try:
        x, y, heading = (finite(value[key]) for key in ('x', 'y', 'heading'))
    except (KeyError, ValueError, TypeError, OverflowError):
        return None
    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= heading < 360):
        return None
    result = {'x': x, 'y': y, 'heading': heading, 'side': 'player'}
    cell = value.get('cell')
    if isinstance(cell, (str, type(u''))) and re.match(r'^[A-HJK][1-90]\Z', cell):
        result['cell'] = cell
    return result


def objective_points(values):
    """Only current, active public map objectives; no arbitrary marker types."""
    if not isinstance(values, list):
        return []
    result = []
    for value in values[:16]:
        if not isinstance(value, dict) or value.get('kind') not in OBJECTIVE_SYMBOLS.values():
            continue
        try:
            x, y = finite(value['x']), finite(value['y'])
        except (KeyError, ValueError, TypeError, OverflowError):
            continue
        if 0 <= x <= 1 and 0 <= y <= 1:
            item = {'x': x, 'y': y, 'kind': value['kind']}
            number = value.get('number')
            if not isinstance(number, bool) and isinstance(number, (int, float)) and 0 <= number <= 99 and int(number) == number:
                item['number'] = int(number)
            state = value.get('state', 'unknown')
            item['state'] = state if state in ('idle', 'capturing', 'blocked', 'captured') else 'unknown'
            try:
                progress = finite(value.get('progress'))
                if item['state'] != 'unknown' and 0 <= progress <= 100:
                    item['progress'] = 100 if item['state'] == 'captured' else progress
            except (ValueError, TypeError, OverflowError):
                pass
            result.append(item)
    return result


RANGE_ADD = {'as_addDrawRange': 'draw', 'as_addDynamicViewRange': 'view',
             'as_addMaxViewRage': 'maxView', 'as_addMinSpottingRange': 'proximity'}
RANGE_REMOVE = {'as_delDrawRange': 'draw', 'as_delDynRange': 'view',
                'as_delMaxViewRage': 'maxView', 'as_delMinSpottingRange': 'proximity'}


def update_ranges(record, signature):
    if not signature:
        return
    circles, method = record['circles'], signature[0]
    if method == 'as_removeAllCircles':
        circles.clear()
    elif method in RANGE_REMOVE:
        circles.pop(RANGE_REMOVE[method], None)
    elif method in RANGE_ADD and len(signature) == 4:
        try:
            color, alpha, radius = [finite(value) for value in signature[1:]]
            if int(color) == color and 0 <= color <= 16777215 and 0 <= alpha <= 100 and 0 < radius <= 100000:
                circles[RANGE_ADD[method]] = {'color': '#%06x' % int(color), 'alpha': alpha / 100, 'radius': radius}
        except (ValueError, TypeError, OverflowError):
            return
    elif method == 'as_updateDynRange' and len(signature) == 2 and 'view' in circles:
        try:
            radius = finite(signature[1])
            if 0 < radius <= 100000:
                circles['view']['radius'] = radius
            else:
                circles.pop('view', None)
        except (ValueError, TypeError, OverflowError):
            circles.pop('view', None)


def circle_points(values):
    result = []
    if not isinstance(values, list):
        return result
    seen = set()
    for value in values[:4]:
        if not isinstance(value, dict) or value.get('kind') not in RANGE_ADD.values() or value['kind'] in seen:
            continue
        try:
            clean = dict((key, finite(value[key])) for key in ('x', 'y', 'rx', 'ry', 'alpha'))
            color = value['color']
            if not (0 <= clean['x'] <= 1 and 0 <= clean['y'] <= 1 and 0 < clean['rx'] <= 100 and
                    0 < clean['ry'] <= 100 and 0 < clean['alpha'] <= 1 and
                    isinstance(color, (str, type(u''))) and re.match(r'^#[0-9a-fA-F]{6}\Z', color)):
                continue
        except (KeyError, ValueError, TypeError, OverflowError):
            continue
        clean.update(kind=value['kind'], color=color)
        seen.add(value['kind'])
        result.append(clean)
    return result
