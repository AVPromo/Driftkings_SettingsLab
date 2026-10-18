# -*- coding: utf-8 -*-
"""Shared crew presentation, without inventory or view lifecycle dependencies."""
from Driftkings.views.marks_model import number_locale


def translated(strings, key):
    value = strings[key]
    return value.decode('utf-8') if isinstance(value, bytes) else value


def integer(value, language):
    return u'{:,}'.format(int(value)).replace(u',', number_locale(language)['groupSeparator'])


def progression_lines(row, settings, language, strings):
    if row['state'] == 'empty':
        return []
    if row['state'] in ('complete', 'ready', 'unavailable'):
        return [translated(strings, 'UI_crew_' + row['state'])]
    lines = []
    if settings.get('showRemainingXP', True):
        key = 'UI_crew_roleXP' if row['roleTraining'] else 'UI_crew_xp'
        lines.append(translated(strings, key).format(xp=integer(row['remainingXP'], language)))
    if settings.get('showEstimatedBattles', True):
        estimate = row['estimatedBattles']
        lines.append(translated(strings, 'UI_crew_noHistory') if estimate is None else
                     translated(strings, 'UI_crew_battles').format(battles=integer(estimate, language)))
    return lines


def progression_kinds(row, settings):
    """Semantic colours shared by native tooltips, details and barracks."""
    if row['state'] == 'empty':
        return []
    if row['state'] != 'training':
        return [row['state']]
    kinds = ['xp'] if settings.get('showRemainingXP', True) else []
    if settings.get('showEstimatedBattles', True):
        kinds.append('battles' if row['estimatedBattles'] is not None else 'unavailable')
    return kinds
