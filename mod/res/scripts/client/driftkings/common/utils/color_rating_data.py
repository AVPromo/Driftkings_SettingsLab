# -*- coding: utf-8 -*-
"""Statistical palettes and threshold tables; no lookup policy."""
from driftkings._constants import MARK_LEVELS as MOE_LEVELS

class ColorRating:
    def __init__(self, scale_name, colors):
        self.scale_name = scale_name
        self.colors = colors

    def table(self):
        return {
            'ScaleColor': self.scale_name,
            'colors': self.colors
        }

noob_meter_definitions = {
    'al': '#22CC00',
    'sq': '#FFB964',
    'tk': '#00EAFF',
    'en': '#F50800',
    'pl': '#FFFF2A',
    'colorRating': {
        'nocolor': '#CCCCCC',
        'very_bad': '#BB0000',
        'bad': '#FF0000',
        'b_average': '#FF6600',
        'average': '#F8F400',
        'normal': '#F8F400',
        'good': '#99CC00',
        'very_good': '#00CC00',
        'great': '#66BBFF',
        'unique': '#CC66CC',
        's_unique': '#FF00FF'
    },
    'colorHP': {
        'very_low': '#FF0000',
        'low': '#DD4444',
        'average': '#FFCC22',
        'above_average': '#EFEFEF'
    }
}

# Team colours by group and state (XVM 'system' scheme). Identical for every
# rating palette, so defined once; the minimap and markers read it from here.
system_colors = {
    'ally_alive': noob_meter_definitions['al'],
    'ally_dead': '#B8FFC1',
    'ally_blowedup': '#007700',
    'squadman_alive': noob_meter_definitions['sq'],
    'squadman_dead': '#CA7000',
    'squadman_blowedup': '#A45A00',
    'teamKiller_alive': noob_meter_definitions['tk'],
    'teamKiller_dead': '#097783',
    'teamKiller_blowedup': '#096A75',
    'enemy_alive': noob_meter_definitions['en'],
    'enemy_dead': '#E29188',
    'enemy_blowedup': '#5A0401',
    'ally_base': noob_meter_definitions['al'],
    'enemy_base': noob_meter_definitions['en']
}

# Vehicle type, total HP and damage log colours are the same in every palette too.
vehicle_type_colors = {
    'LT': '#53B329',
    'MT': '#1EA2D2',
    'HT': '#957D5B',
    'SPG': '#B87AB2',
    'TD': '#F13439',
    'premium': '#FFA804',
    'usePremiumColor': False
}

total_hp_colors = {
    'bad': '#FF0000',
    'neutral': '#FFFFFF',
    'good': '#00FF00'
}

damage_colors = {
    'ally_ally_hit': noob_meter_definitions['tk'],
    'ally_ally_kill': noob_meter_definitions['tk'],
    'ally_ally_blowup': noob_meter_definitions['tk'],
    'ally_squadman_hit': noob_meter_definitions['tk'],
    'ally_squadman_kill': noob_meter_definitions['tk'],
    'ally_squadman_blowup': noob_meter_definitions['tk'],
    'ally_enemy_hit': noob_meter_definitions['en'],
    'ally_enemy_kill': noob_meter_definitions['en'],
    'ally_enemy_blowup': noob_meter_definitions['en'],
    'ally_allytk_hit': noob_meter_definitions['tk'],
    'ally_allytk_kill': noob_meter_definitions['tk'],
    'ally_allytk_blowup': noob_meter_definitions['tk'],
    'ally_enemytk_hit': noob_meter_definitions['en'],
    'ally_enemytk_kill': noob_meter_definitions['en'],
    'ally_enemytk_blowup': noob_meter_definitions['en'],
    'enemy_ally_hit': noob_meter_definitions['al'],
    'enemy_ally_kill': noob_meter_definitions['al'],
    'enemy_ally_blowup': noob_meter_definitions['al'],
    'enemy_squadman_hit': noob_meter_definitions['al'],
    'enemy_squadman_kill': noob_meter_definitions['al'],
    'enemy_squadman_blowup': noob_meter_definitions['al'],
    'enemy_enemy_hit': noob_meter_definitions['en'],
    'enemy_enemy_kill': noob_meter_definitions['en'],
    'enemy_enemy_blowup': noob_meter_definitions['en'],
    'enemy_allytk_hit': noob_meter_definitions['al'],
    'enemy_allytk_kill': noob_meter_definitions['al'],
    'enemy_allytk_blowup': noob_meter_definitions['al'],
    'enemy_enemytk_hit': noob_meter_definitions['en'],
    'enemy_enemytk_kill': noob_meter_definitions['en'],
    'enemy_enemytk_blowup': noob_meter_definitions['en'],
    'unknown_ally_hit': noob_meter_definitions['al'],
    'unknown_ally_kill': noob_meter_definitions['al'],
    'unknown_ally_blowup': noob_meter_definitions['al'],
    'unknown_squadman_hit': noob_meter_definitions['al'],
    'unknown_squadman_kill': noob_meter_definitions['al'],
    'unknown_squadman_blowup': noob_meter_definitions['al'],
    'unknown_enemy_hit': noob_meter_definitions['en'],
    'unknown_enemy_kill': noob_meter_definitions['en'],
    'unknown_enemy_blowup': noob_meter_definitions['en'],
    'unknown_allytk_hit': noob_meter_definitions['al'],
    'unknown_allytk_kill': noob_meter_definitions['al'],
    'unknown_allytk_blowup': noob_meter_definitions['al'],
    'unknown_enemytk_hit': noob_meter_definitions['en'],
    'unknown_enemytk_kill': noob_meter_definitions['en'],
    'unknown_enemytk_blowup': noob_meter_definitions['en'],
    'squadman_ally_hit': noob_meter_definitions['sq'],
    'squadman_ally_kill': noob_meter_definitions['sq'],
    'squadman_ally_blowup': noob_meter_definitions['sq'],
    'squadman_squadman_hit': noob_meter_definitions['sq'],
    'squadman_squadman_kill': noob_meter_definitions['sq'],
    'squadman_squadman_blowup': noob_meter_definitions['sq'],
    'squadman_enemy_hit': noob_meter_definitions['sq'],
    'squadman_enemy_kill': noob_meter_definitions['sq'],
    'squadman_enemy_blowup': noob_meter_definitions['sq'],
    'squadman_allytk_hit': noob_meter_definitions['sq'],
    'squadman_allytk_kill': noob_meter_definitions['sq'],
    'squadman_allytk_blowup': noob_meter_definitions['sq'],
    'squadman_enemytk_hit': noob_meter_definitions['sq'],
    'squadman_enemytk_kill': noob_meter_definitions['sq'],
    'squadman_enemytk_blowup': noob_meter_definitions['sq'],
    'player_ally_hit': noob_meter_definitions['pl'],
    'player_ally_kill': noob_meter_definitions['pl'],
    'player_ally_blowup': noob_meter_definitions['pl'],
    'player_squadman_hit': noob_meter_definitions['pl'],
    'player_squadman_kill': noob_meter_definitions['pl'],
    'player_squadman_blowup': noob_meter_definitions['pl'],
    'player_enemy_hit': noob_meter_definitions['pl'],
    'player_enemy_kill': noob_meter_definitions['pl'],
    'player_enemy_blowup': noob_meter_definitions['pl'],
    'player_allytk_hit': noob_meter_definitions['pl'],
    'player_allytk_kill': noob_meter_definitions['pl'],
    'player_allytk_blowup': noob_meter_definitions['pl'],
    'player_enemytk_hit': noob_meter_definitions['pl'],
    'player_enemytk_kill': noob_meter_definitions['pl'],
    'player_enemytk_blowup': noob_meter_definitions['pl']
}

noob_meter_colors = {
    'colorRating': noob_meter_definitions['colorRating'],
    'colorHP': noob_meter_definitions['colorHP'],
    'system': system_colors,
    'dmg_kind': {
        'attack': '#FFAA55',
        'fire': '#FF6655',
        'ramming': '#00CCCC',
        'world_collision': '#998855',
        'other': '#CCCCCC'
    },
    'vtype': vehicle_type_colors,
    'spotted': {
        'neverSeen': '#000000',
        'lost': '#FF552A',
        'spotted': '#FFBB00',
        'dead': '#FFFFFF',
        'neverSeen_arty': '#000000',
        'lost_arty': '#D9D9D9',
        'spotted_arty': '#FFBB00',
        'dead_arty': '#FFFFFF'
    },
    'totalHP': total_hp_colors,
    'damage': damage_colors,
    'hp': [
        {'value': 201, 'color': noob_meter_definitions['colorHP']['very_low']},
        {'value': 401, 'color': noob_meter_definitions['colorHP']['low']},
        {'value': 1001, 'color': noob_meter_definitions['colorHP']['average']},
        {'value': 9999, 'color': noob_meter_definitions['colorHP']['above_average']}
    ],
    'hp_ratio': [
        {'value': 10, 'color': noob_meter_definitions['colorHP']['very_low']},
        {'value': 25, 'color': noob_meter_definitions['colorHP']['low']},
        {'value': 50, 'color': noob_meter_definitions['colorHP']['average']},
        {'value': 101, 'color': noob_meter_definitions['colorHP']['above_average']}
    ],
    'x': [
        {'value': 16.5, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 33.5, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 52.5, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 75.5, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 92.5, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'eff': [
        {'value': 615, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 870, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 1175, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1525, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 1850, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 9999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'wtr': [
        {'value': 2631, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 4464, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 6249, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 8141, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 9460, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'wn8': [
        {'value': 300, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 600, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 900, 'color': noob_meter_definitions['colorRating']['b_average']},
        {'value': 1200, 'color': noob_meter_definitions['colorRating']['average']},
        {'value': 1500, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 1750, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 2300, 'color': noob_meter_definitions['colorRating']['great']},
        {'value': 2900, 'color': noob_meter_definitions['colorRating']['unique']},
        {'value': 9999, 'color': noob_meter_definitions['colorRating']['s_unique']}
    ],
    'wgr': [
        {'value': 2020, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 4185, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 6340, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 8525, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 9930, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'e': [
        {'value': 3, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 6, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 7, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 8, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 9, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 20, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'winrate': [
        {'value': 43, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 45, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 47, 'color': noob_meter_definitions['colorRating']['average']},
        {'value': 51, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 53, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 55, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 59, 'color': noob_meter_definitions['colorRating']['great']},
        {'value': 93, 'color': noob_meter_definitions['colorRating']['unique']},
        {'value': 101, 'color': noob_meter_definitions['colorRating']['s_unique']}
    ],
    'kb': [
        {'value': 2, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 6, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 16, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 30, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 43, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'avglvl': [
        {'value': 1, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 2, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 4, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 6, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 8, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 10, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    't_battles': [
        {'value': 100, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 250, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 500, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1000, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 1800, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'tdb': [
        {'value': 500, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 750, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 1000, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1800, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 2500, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 9999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'tdv': [
        {'value': 0.6, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 2.0, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 15, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'tfb': [
        {'value': 0.6, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 2.0, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 15, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'tsb': [
        {'value': 0.6, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 2.0, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 15, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'wn8effd': [
        {'value': 0.6, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 2.0, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 15, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'dmg_ratio_player': [
        {'value': 16.5, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 33.5, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 49.5, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 66.5, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 83.5, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 999, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'damageRating': [
        {'value': 20, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 60, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 90, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 99, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 99.9, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 101, 'color': noob_meter_definitions['colorRating']['unique']}
    ],
    'hitsRatio': [
        {'value': 47.5, 'color': noob_meter_definitions['colorRating']['very_bad']},
        {'value': 60.5, 'color': noob_meter_definitions['colorRating']['bad']},
        {'value': 68.5, 'color': noob_meter_definitions['colorRating']['normal']},
        {'value': 74.5, 'color': noob_meter_definitions['colorRating']['good']},
        {'value': 78.5, 'color': noob_meter_definitions['colorRating']['very_good']},
        {'value': 101, 'color': noob_meter_definitions['colorRating']['unique']}
    ]
}


# XVM: xvm_scale/colors.xc

xvm_definitions = {
    'al': '#22CC00',
    'sq': '#FFB964',
    'tk': '#00EAFF',
    'en': '#F50800',
    'pl': '#FFFF2A',
    'colorRating': {
        'very_bad': '#FE0E00',
        'bad': '#FE7903',
        'normal': '#F8F400',
        'good': '#60FF00',
        'very_good': '#02C9B3',
        'unique': '#D042F3'
    },
    'colorHP': {
        'very_low': '#FF0000',
        'low': '#DD4444',
        'average': '#FFCC22',
        'above_average': '#FCFCFC'
    }
}

xvm_colors = {
    'colorRating': xvm_definitions['colorRating'],
    'colorHP': xvm_definitions['colorHP'],
    'system': system_colors,
    'dmg_kind': {
        'attack': '#FFAA55',
        'fire': '#FF6655',
        'ramming': '#00CCCC',
        'world_collision': '#998855',
        'death_zone': '#CCCCCC',
        'drowning': '#CCCCCC',
        'other': '#CCCCCC'
    },
    'vtype': vehicle_type_colors,
    'spotted': {
        'neverSeen': '#000000',
        'lost': '#FF552A',
        'spotted': '#FFBB00',
        'dead': '#FFFFFF',
        'neverSeen_arty': '#000000',
        'lost_arty': '#D9D9D9',
        'spotted_arty': '#FFBB00',
        'dead_arty': '#FFFFFF'
    },
    'totalHP': total_hp_colors,
    'damage': damage_colors,
    'hp': [
        {'value': 200, 'color': xvm_definitions['colorHP']['very_low']},
        {'value': 400, 'color': xvm_definitions['colorHP']['low']},
        {'value': 1000, 'color': xvm_definitions['colorHP']['average']},
        {'value': 9999, 'color': xvm_definitions['colorHP']['above_average']}
    ],
    'hp_ratio': [
        {'value': 10.4, 'color': xvm_definitions['colorHP']['very_low']},
        {'value': 25.4, 'color': xvm_definitions['colorHP']['low']},
        {'value': 50.4, 'color': xvm_definitions['colorHP']['average']},
        {'value': 100, 'color': xvm_definitions['colorHP']['above_average']}
    ],
    'x': [
        {'value': 16.4, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 33.4, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 52.4, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 75.4, 'color': xvm_definitions['colorRating']['good']},
        {'value': 92.4, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'eff': [
        {'value': 598, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 874, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 1079, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 1540, 'color': xvm_definitions['colorRating']['good']},
        {'value': 1868, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 9999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'wtr': [
        {'value': 2631, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 4464, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 6249, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 8141, 'color': xvm_definitions['colorRating']['good']},
        {'value': 9460, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'wn8': [
        {'value': 397, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 914, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 1489, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 2231, 'color': xvm_definitions['colorRating']['good']},
        {'value': 2979, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 9999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'winrate': [
        {'value': 46.49, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 48.49, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 52.49, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 57.49, 'color': xvm_definitions['colorRating']['good']},
        {'value': 64.49, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 100, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'kb': [
        {'value': 2, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 6, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 16, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 30, 'color': xvm_definitions['colorRating']['good']},
        {'value': 43, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'avglvl': [
        {'value': 1, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 2, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 4, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 6, 'color': xvm_definitions['colorRating']['good']},
        {'value': 8, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 10, 'color': xvm_definitions['colorRating']['unique']}
    ],
    't_battles': [
        {'value': 99, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 249, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 499, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 999, 'color': xvm_definitions['colorRating']['good']},
        {'value': 1799, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'tdb': [
        {'value': 499, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 749, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 999, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 1799, 'color': xvm_definitions['colorRating']['good']},
        {'value': 2499, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 9999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'tdv': [
        {'value': 0.5, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 0.7, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 0.9, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 1.2, 'color': xvm_definitions['colorRating']['good']},
        {'value': 1.9, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 15, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'tfb': [
        {'value': 0.5, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 0.7, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 0.9, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 1.2, 'color': xvm_definitions['colorRating']['good']},
        {'value': 1.9, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 15, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'tsb': [
        {'value': 0.5, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 0.7, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 0.9, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 1.2, 'color': xvm_definitions['colorRating']['good']},
        {'value': 1.9, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 15, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'wn8effd': [
        {'value': 0.5, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 0.7, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 0.9, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 1.2, 'color': xvm_definitions['colorRating']['good']},
        {'value': 1.9, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 15, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'dmg_ratio_player': [
        {'value': 16.5, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 33.5, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 49.5, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 66.5, 'color': xvm_definitions['colorRating']['good']},
        {'value': 83.5, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 999, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'damageRating': [
        {'value': 64.99, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 84.99, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 94.99, 'color': xvm_definitions['colorRating']['good']},
        {'value': 100, 'color': xvm_definitions['colorRating']['unique']}
    ],
    'hitsRatio': [
        {'value': 47.4, 'color': xvm_definitions['colorRating']['very_bad']},
        {'value': 60.4, 'color': xvm_definitions['colorRating']['bad']},
        {'value': 68.4, 'color': xvm_definitions['colorRating']['normal']},
        {'value': 74.4, 'color': xvm_definitions['colorRating']['good']},
        {'value': 78.4, 'color': xvm_definitions['colorRating']['very_good']},
        {'value': 100, 'color': xvm_definitions['colorRating']['unique']}
    ]
}


# WotLabs: wotlabs_scale/colors.xc

wot_labs_definitions = {
    'al': '#22CC00',
    'sq': '#FFB964',
    'tk': '#00EAFF',
    'en': '#F50800',
    'pl': '#FFFF2A',
    'colorRating': {
        'nocolor': '#CCCCCC',
        'very_bad': '#BB0000',
        'bad': '#FF0000',
        'b_average': '#FF6600',
        'average': '#F8F400',
        'normal': '#F8F400',
        'good': '#99CC00',
        'very_good': '#00CC00',
        'great': '#66BBFF',
        'unique': '#CC66CC',
        's_unique': '#FF00FF'
    },
    'colorRatingNew': {
        'beginner': '#C00B00',
        'basic': '#f11919',
        'below_average': '#ff8a00',
        'average': '#e6df27',
        'above_average': '#77e812',
        'good': '#459300',
        'very_good': '#2ae4ff',
        'great': '#00a0b8',
        'unicum': '#c64cff',
        'super_unicum': '#8225ad'
    },
    'colorHP': {
        'very_low': '#FF0000',
        'low': '#DD4444',
        'average': '#FFCC22',
        'above_average': '#FCFCFC'
    }
}

# Source winrate refers to three missing colorRating names.
# below_average, above_average and super_unicum use colorRatingNew.

wot_labs_colors = {
    'colorRating': wot_labs_definitions['colorRating'],
    'colorRatingNew': wot_labs_definitions['colorRatingNew'],
    'colorHP': wot_labs_definitions['colorHP'],
    'system': system_colors,
    'dmg_kind': {
        'attack': '#FFAA55',
        'fire': '#FF6655',
        'ramming': '#00CCCC',
        'world_collision': '#998855',
        'death_zone': '#CCCCCC',
        'drowning': '#CCCCCC',
        'other': '#CCCCCC'
    },
    'vtype': vehicle_type_colors,
    'spotted': {
        'neverSeen': '#000000',
        'lost': '#D9D9D9',
        'spotted': '#FFBB00',
        'dead': '#FFFFFF',
        'neverSeen_arty': '#000000',
        'lost_arty': '#D9D9D9',
        'spotted_arty': '#FFBB00',
        'dead_arty': '#FFFFFF'
    },
    'totalHP': total_hp_colors,
    'damage': damage_colors,
    'hp': [
        {'value': 201, 'color': wot_labs_definitions['colorHP']['very_low']},
        {'value': 401, 'color': wot_labs_definitions['colorHP']['low']},
        {'value': 1001, 'color': wot_labs_definitions['colorHP']['average']},
        {'value': 9999, 'color': wot_labs_definitions['colorHP']['above_average']}
    ],
    'hp_ratio': [
        {'value': 10, 'color': wot_labs_definitions['colorHP']['very_low']},
        {'value': 25, 'color': wot_labs_definitions['colorHP']['low']},
        {'value': 50, 'color': wot_labs_definitions['colorHP']['average']},
        {'value': 101, 'color': wot_labs_definitions['colorHP']['above_average']}
    ],
    'x': [
        {'value': 16.5, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 33.5, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 52.5, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 75.5, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 92.5, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 999, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'eff': [
        {'value': 610, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 850, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 1145, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1475, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 1775, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 9999, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'wtr': [
        {'value': 2631, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 4464, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 6249, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 8141, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 9460, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'wn8': [
        {'value': 300, 'color': wot_labs_definitions['colorRatingNew']['beginner']},
        {'value': 450, 'color': wot_labs_definitions['colorRatingNew']['basic']},
        {'value': 650, 'color': wot_labs_definitions['colorRatingNew']['below_average']},
        {'value': 900, 'color': wot_labs_definitions['colorRatingNew']['average']},
        {'value': 1200, 'color': wot_labs_definitions['colorRatingNew']['above_average']},
        {'value': 1600, 'color': wot_labs_definitions['colorRatingNew']['good']},
        {'value': 2000, 'color': wot_labs_definitions['colorRatingNew']['very_good']},
        {'value': 2450, 'color': wot_labs_definitions['colorRatingNew']['great']},
        {'value': 2900, 'color': wot_labs_definitions['colorRatingNew']['unicum']},
        {'value': 9999, 'color': wot_labs_definitions['colorRatingNew']['super_unicum']}
    ],
    'wgr': [
        {'value': 2000, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 4000, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 6000, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 8000, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 10000, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 20000, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'e': [
        {'value': 3, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 6, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 7, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 8, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 9, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 20, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'winrate': [
        {'value': 46, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 47, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 48, 'color': wot_labs_definitions['colorRatingNew']['below_average']},
        {'value': 50, 'color': wot_labs_definitions['colorRating']['average']},
        {'value': 52, 'color': wot_labs_definitions['colorRatingNew']['above_average']},
        {'value': 54, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 56, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 60, 'color': wot_labs_definitions['colorRating']['great']},
        {'value': 65, 'color': wot_labs_definitions['colorRating']['unique']},
        {'value': 101, 'color': wot_labs_definitions['colorRatingNew']['super_unicum']}
    ],
    'kb': [
        {'value': 2, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 5, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 9, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 14, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 20, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 999, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'avglvl': [
        {'value': 2, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 3, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 5, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 7, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 9, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 11, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    't_battles': [
        {'value': 100, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 250, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 500, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1000, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 1800, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 99999, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'tdb': [
        {'value': 500, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 1000, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1800, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 2500, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 3000, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'tdv': [
        {'value': 0.6, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 2.0, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 15, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'tfb': [
        {'value': 0.6, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 2.0, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 15, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'tsb': [
        {'value': 0.6, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 2.0, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 15, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'wn8effd': [
        {'value': 0.6, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 0.8, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 1.0, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 1.3, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 2.0, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 15, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'dmg_ratio_player': [
        {'value': 16.5, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 33.5, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 49.5, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 66.5, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 83.5, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 999, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'damageRating': [
        {'value': 64.99, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 84.99, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 94.99, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 100, 'color': wot_labs_definitions['colorRating']['unique']}
    ],
    'hitsRatio': [
        {'value': 47.5, 'color': wot_labs_definitions['colorRating']['very_bad']},
        {'value': 60.5, 'color': wot_labs_definitions['colorRating']['bad']},
        {'value': 68.5, 'color': wot_labs_definitions['colorRating']['normal']},
        {'value': 74.5, 'color': wot_labs_definitions['colorRating']['good']},
        {'value': 78.5, 'color': wot_labs_definitions['colorRating']['very_good']},
        {'value': 100, 'color': wot_labs_definitions['colorRating']['unique']}
    ]
}


# Project statistics absent from XVM: keep all limits and palette decisions here.
for _table in (noob_meter_colors, xvm_colors, wot_labs_colors):
    _palette = _table['colorRating']
    # Driftkings profile scales, not XVM rating thresholds.
    _table['survival'] = [{'value': limit, 'color': _palette[name]} for limit, name in zip(
        (20, 30, 40, 50, 60, 1e30), ('very_bad', 'bad', 'normal', 'good', 'very_good', 'unique'))]
    # Lower received damage / vehicle HP is better; raw HP is tier-dependent.
    _table['damageReceivedHP'] = [{'value': limit, 'color': _palette[name]} for limit, name in zip(
        (.25, .5, .75, 1.0, 1.25, 1e30), ('unique', 'very_good', 'good', 'normal', 'bad', 'very_bad'))]
    _table['mog'] = [{'value': limit, 'color': _palette.get(name, _palette['unique']) if name != 'neutral' else '#FFFFFF'} for limit, name in zip(MOE_LEVELS, ('neutral', 'very_bad', 'bad', 'normal', 'good', 'very_good', 'unique', 's_unique'))]
    for _metric in ('damageRatio', 'damageHP', 'relativePerformance'):
        _table[_metric] = [{'value': limit, 'color': _palette[name]} for limit, name in zip((0.5, 0.75, 1.0, 1.5, 2.0, 1e30), ('very_bad', 'bad', 'normal', 'good', 'very_good', 'unique'))]
    _table['diff'] = [
        {'value': 0, 'color': _palette['very_bad']},
        {'value': 0, 'color': _palette['normal']},
        {'value': 1e30, 'color': _palette['good']}
    ]
del _table, _palette, _metric


color_tables = [
    ColorRating('NoobMeter', noob_meter_colors).table(),
    ColorRating('XVM', xvm_colors).table(),
    ColorRating('WotLabs', wot_labs_colors).table()
]
