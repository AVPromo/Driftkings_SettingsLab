# -*- coding: utf-8 -*-
"""Presentation only: receives calculated MoE values, never acquires game data."""
from Driftkings.common.utils.numbers import finite_number as finite
from Driftkings._constants import MARK_THRESHOLDS
from Driftkings.locale_support import language_code


def number_locale(language):
    """Number presentation for the same supported language as the panel labels."""
    code = language_code(language)
    if code in ('de', 'es', 'it', 'tr', 'vi'):
        decimal, group = ',', '.'
    elif code in ('cs', 'fr', 'hu', 'pl', 'pt', 'ru', 'uk'):
        decimal, group = ',', u'\u00a0'
    else:
        decimal, group = '.', ','
    return {'decimalSeparator': decimal, 'groupSeparator': group}



def delta_model(value):
    value = finite(value)
    if value is None:
        return {'text': u'\u2014', 'direction': 'unknown'}
    value = round(value, 2)
    direction = 'positive' if value > 0 else 'negative' if value < 0 else 'zero'
    symbol = u'\u25b2' if value > 0 else u'\u25bc' if value < 0 else u'\u2014'
    return {'text': symbol + ' ' + ('%+.2f%%' % value if value else '0.00%'), 'direction': direction}


def milestone_model(percent, earned=0):
    """Progress inside the next excellence interval, never percent/100."""
    percent = finite(percent)
    if percent is None:
        return {'nextMilestone': None, 'progress': 0, 'gap': None, 'completed': False}
    percent = max(0.0, min(100.0, percent))
    thresholds = MARK_THRESHOLDS
    achieved = max(int(finite(earned, 0)), sum(percent >= value for value in thresholds))
    if achieved >= 3:
        return {'nextMilestone': None, 'progress': 1, 'gap': 0, 'completed': True}
    low = (0, 65, 85)[achieved]
    high = thresholds[achieved]
    return {'nextMilestone': high, 'progress': max(0.0, min(1.0, (percent - low) / (high - low))),
            'gap': max(0.0, high - percent), 'completed': False}


def compact_model(vehicle_id, current, estimated, damage, assists, targets, earned=0, valid=True):
    """All numeric values are supplied by the calculation engine, not JS."""
    current, estimated = finite(current), finite(estimated)
    valid = bool(valid and current is not None and estimated is not None)
    result = {'state': 'data' if valid else 'unavailable', 'vehicleId': vehicle_id,
              'currentMark': current, 'estimatedMark': estimated if valid else None,
              'marksAchieved': max(0, min(3, int(finite(earned, 0)))),
              'directDamage': finite(damage, 0), 'assistance': list(assists),
              'combinedDamage': finite(damage, 0) + max(assists),
              'trend': delta_model(estimated - current if valid else None)}
    result.update(milestone_model(estimated if valid else None, earned))
    target = targets.get(result['nextMilestone']) if valid else None
    result['targetDamage'] = target
    result['damageNeeded'] = max(0, target - result['combinedDamage']) if target is not None else None
    return result
