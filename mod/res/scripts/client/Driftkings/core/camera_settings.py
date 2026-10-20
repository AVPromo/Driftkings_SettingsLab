# -*- coding: utf-8 -*-
"""Mode-specific camera options and migration, independent of the client."""
import math
from Driftkings._constants import THIRD_PERSON_ZOOM


def migrate(values):
    old = dict((key, values.pop(key)) for key in
               ('min', 'max', 'scrollSensitivity', 'startDeadDist') if key in values)
    if old:
        for mode in ('arcade', 'postmortem'):
            options = values.setdefault(mode, {})
            explicit_start = 'startDist' in options
            for key, value in old.items():
                options.setdefault('startDist' if key == 'startDeadDist' else key, value)
            # The old panel allowed a start outside its distance range. Native
            # camera code clamped it; preserve a loadable profile on migration.
            low, high = options.get('min', 10), options.get('max', 400)
            start = options.setdefault('startDist', 60)
            if (not explicit_start and all(type(value) in (int, float) for value in (low, high, start))
                    and not any(math.isnan(value) or math.isinf(value) for value in (low, high, start))
                    and low <= high):
                options['startDist'] = max(low, min(high, start))
    return values


def validate(values):
    for mode in THIRD_PERSON_ZOOM.MODES:
        options = values[mode]
        for key in ('min', 'max', 'scrollSensitivity'):
            value = options[key]
            if type(value) not in (int, float) or math.isnan(value) or math.isinf(value):
                raise ValueError('Invalid camera value: ' + mode + '.' + key)
        if not 1 <= options['min'] <= options['max'] <= 450:
            raise ValueError('Invalid camera distance range: ' + mode)
        if not 1 <= options['scrollSensitivity'] <= 100:
            raise ValueError('Invalid camera scroll sensitivity: ' + mode)
        if mode in ('arcade', 'postmortem'):
            value = options['startDist']
            if type(value) not in (int, float) or not options['min'] <= value <= options['max']:
                raise ValueError('Start distance must be inside the camera range: ' + mode)
        elif type(options['useClientDefaults']) is not bool:
            raise ValueError('Invalid native camera switch: ' + mode)
    return values


def options(values, mode):
    if not values['enabled']:
        return None
    result = values[mode]
    return None if result.get('useClientDefaults', False) else result
