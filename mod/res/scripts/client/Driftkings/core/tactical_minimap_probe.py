# -*- coding: utf-8 -*-
"""Small diagnostic transport contract. Never publishes vehicle identities/positions."""
from Driftkings.core.tactical_minimap import finite

PROTOCOL = 1


def payload(enabled, acknowledged, snapshot=None, generation=0, graphics=None):
    data = {'enabled': bool(enabled), 'protocol': PROTOCOL, 'generation': generation, 'effectiveMode': 'vanilla',
            'acknowledged': bool(acknowledged), 'nativePresentationChanged': False,
            'available': False, 'partial': True, 'markerCount': 0,
            'reason': 'waiting-native', 'lostContactAvailable': False}
    if not enabled:
        data['reason'] = 'disabled'
        return data
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
