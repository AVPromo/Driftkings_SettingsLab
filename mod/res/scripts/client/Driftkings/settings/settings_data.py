# -*- coding: utf-8 -*-
"""Settings metadata and access to JSON-generated component defaults."""
import copy

from Driftkings._constants import (
    ACCOUNT_MANAGER, AIMING_ANGLES, ARCADE_ZOOM, ARMOR_CALCULATOR,
    ARTY_SPLASH, AUTO_AIM_OPTIMIZE, AUTO_CLAIM_CLAN, BANKS_LOADER,
    BATTLE_EFFICIENCY, BATTLE_OPTIONS, BATTLE_STAT, CAROUSEL_STATS,
    CREW_SETTINGS, DISPERSION_CIRCLE, DISPERSION_TIMER,
    DISTANCE_MARKER, FLIGHT_TIMER, GLOBAL, HANGAR_OPTIONS,
    INFO_PANEL, LOGS_SWAPPER, MAIN_GUN, MARKS_ON_GUN_BATTLE,
    MARKS_ON_GUN_HANGAR, MARKS_ON_GUN_TECH_TREE, MINIMAP_PLUGINS, OWN_HEALTH,
    PLAYER_PANEL_PRO, REPAIR_EXTENDED, SAFE_SHOT, SERVER_TURRET_EXTENDED,
    SIXTH_SENSE, SPOTTED_EXTENDED_LIGHT, ZOOM_EXTENDED,)

from Driftkings.settings.default_values import DEFAULTS
from Driftkings.settings.sections import section_name

# Only the field names are policy; key bindings come from the JSON.
HOTKEY_FIELDS = {
    ARTY_SPLASH.NAME: (ARTY_SPLASH.BUTTON_SHOW_DOT, ARTY_SPLASH.BUTTON_SHOW_SPLASH),
    INFO_PANEL.NAME: (INFO_PANEL.ALT_KEY,),
    MARKS_ON_GUN_BATTLE.NAME: (MARKS_ON_GUN_BATTLE.BUTTON_SHOW, MARKS_ON_GUN_BATTLE.BUTTON_SIZE_UP,
                           MARKS_ON_GUN_BATTLE.BUTTON_SIZE_DOWN, MARKS_ON_GUN_BATTLE.BUTTON_RESET),
    MINIMAP_PLUGINS.NAME: (MINIMAP_PLUGINS.BUTTON,),
    REPAIR_EXTENDED.NAME: (REPAIR_EXTENDED.BUTTON_REPAIR, REPAIR_EXTENDED.BUTTON_CHASSIS),
    SAFE_SHOT.NAME: (SAFE_SHOT.DISABLE_KEY,),
    SERVER_TURRET_EXTENDED.NAME: (SERVER_TURRET_EXTENDED.BUTTON_AUTO_MODE, SERVER_TURRET_EXTENDED.BUTTON_MAX_MODE),
}
HOTKEYS = dict((component, dict((key, copy.deepcopy(DEFAULTS[component][key])) for key in fields))
               for component, fields in HOTKEY_FIELDS.items())
PROFILES = ('none', 'short', 'medium', 'medium2', 'large')


def defaults(component):
    return copy.deepcopy(DEFAULTS[section_name(component)])


def default_keys(component):
    return copy.deepcopy(HOTKEYS.get(section_name(component), {}))


def part_name(component):
    return section_name(component)


def profile_for_mode(mode):
    # Native EU PLAYERS_PANEL_STATE, including variants without badges.
    return {0: 'none', 1: 'short', 20: 'short', 2: 'medium', 5: 'medium',
            3: 'medium2', 21: 'medium2', 4: 'large', 6: 'large'}.get(mode, 'large')


class SettingsData(object):
    """Shared access to the same live dictionaries used by feature controllers."""
    def __init__(self):
        self.configs = {}

    def register(self, config):
        self.configs[part_name(config.NAME)] = config

    def __getattr__(self, name):
        config = self.configs.get(name)
        if config is None:
            raise AttributeError(name)
        return config.data


user_settings = SettingsData()

# Controllers verified to read or refresh these values during battle.
BATTLE_EDITABLE = frozenset((AUTO_AIM_OPTIMIZE.NAME, SAFE_SHOT.NAME, INFO_PANEL.NAME, PLAYER_PANEL_PRO.NAME))
# Application timing follows the readers/callbacks in each controller. Unknown
# options retain the safe restart policy; paths allow different nested options.
LIVE = 'live'
NEXT_BATTLE = 'battle'
NEXT_VIEW = 'view'
RESTART = 'restart'
APPLY_TIMING = {
    AUTO_AIM_OPTIMIZE.NAME: {'*': LIVE},  # lock request reads the current dictionary
    SAFE_SHOT.NAME: {'*': LIVE},        # shot handler reads the current dictionary
    INFO_PANEL.NAME: {'*': LIVE, GLOBAL.ENABLED: NEXT_BATTLE},
    PLAYER_PANEL_PRO.NAME: {'*': LIVE, GLOBAL.ENABLED: NEXT_BATTLE},
    MAIN_GUN.NAME: {GLOBAL.ENABLED: LIVE, MAIN_GUN.BACK_GROUND_ENABLED: LIVE, MAIN_GUN.TEXT_LOCK: LIVE, MAIN_GUN.TEXT_POSITION: LIVE, 'background.alpha': LIVE},
    BATTLE_STAT.NAME: {GLOBAL.ENABLED: LIVE, BATTLE_STAT.FORMAT: LIVE, BATTLE_STAT.COLOR_RATING: LIVE, BATTLE_STAT.TEXT_LOCK: LIVE, BATTLE_STAT.TEXT_POSITION: LIVE},
    BATTLE_EFFICIENCY.NAME: {GLOBAL.ENABLED: NEXT_BATTLE, BATTLE_EFFICIENCY.TEXT_LOCK: LIVE, BATTLE_EFFICIENCY.POSITION: LIVE, BATTLE_EFFICIENCY.COLOR_RATTING: LIVE, BATTLE_EFFICIENCY.FORMAT: LIVE, BATTLE_EFFICIENCY.BATTLE_RESULTS_WINDOW: NEXT_VIEW, BATTLE_EFFICIENCY.BATTLE_RESULTS_FORMAT: NEXT_VIEW},
    OWN_HEALTH.NAME: {'*': LIVE, GLOBAL.ENABLED: NEXT_BATTLE},
    # Views/cameras are constructed again when entering battle.
    ARMOR_CALCULATOR.NAME: {'*': NEXT_BATTLE},
    ARTY_SPLASH.NAME: {'*': NEXT_BATTLE},
    # Arcade camera base dictionaries are shared and cleared only on first use.
    ARCADE_ZOOM.NAME: {'*': RESTART},
    DISPERSION_TIMER.NAME: {'*': NEXT_BATTLE},
    FLIGHT_TIMER.NAME: {'*': NEXT_BATTLE},
    DISTANCE_MARKER.NAME: {'*': NEXT_BATTLE},
    SIXTH_SENSE.NAME: {'*': NEXT_BATTLE},
    DISPERSION_CIRCLE.NAME: {'*': NEXT_BATTLE},
    MINIMAP_PLUGINS.NAME: {'*': NEXT_BATTLE},
    BATTLE_OPTIONS.NAME: {'*': NEXT_BATTLE},
    MARKS_ON_GUN_BATTLE.NAME: {'*': NEXT_BATTLE},
    AIMING_ANGLES.NAME: {'*': NEXT_BATTLE},
    SPOTTED_EXTENDED_LIGHT.NAME: {'*': NEXT_BATTLE},
    SERVER_TURRET_EXTENDED.NAME: {'*': NEXT_BATTLE},
    REPAIR_EXTENDED.NAME: {'*': NEXT_BATTLE},
    LOGS_SWAPPER.NAME: {'*': LIVE},  # filters/routing read on each new log entry
    CREW_SETTINGS.NAME: {'*': NEXT_VIEW},  # vehicle selection/crew action
    AUTO_CLAIM_CLAN.NAME: {'*': NEXT_VIEW},
    ACCOUNT_MANAGER.NAME: {'*': NEXT_VIEW},  # next login window
    CAROUSEL_STATS.NAME: {'*': LIVE},  # controller.onApplySettings
    MARKS_ON_GUN_HANGAR.NAME: {'*': LIVE},
    MARKS_ON_GUN_TECH_TREE.NAME: {'*': LIVE},
    HANGAR_OPTIONS.NAME: {'*': NEXT_VIEW, HANGAR_OPTIONS.LOW_AMMO_PERCENTAGE: LIVE, HANGAR_OPTIONS.SHOW_BATTLE_PASS_WIDGET: LIVE, HANGAR_OPTIONS.CLOCK: LIVE, HANGAR_OPTIONS.CLOCK_X: LIVE, HANGAR_OPTIONS.CLOCK_Y: LIVE, HANGAR_OPTIONS.CLOCK_SCALE: LIVE, HANGAR_OPTIONS.CUSTOM_CLOCK_TEXT: RESTART, 'showBuyPremiumButton': RESTART, 'showPremiumShopButton': NEXT_VIEW, 'showReferralButton': NEXT_VIEW, 'showWotPlusButton': RESTART, 'premiumTime': RESTART, HANGAR_OPTIONS.HIDE_BTN_COUNTERS: LIVE},
    # The camera-change listener caches these values only at construction.
    ZOOM_EXTENDED.NAME: {ZOOM_EXTENDED.NO_BINOCULARS: NEXT_BATTLE, ZOOM_EXTENDED.NO_SNIPER_DYNAMIC: NEXT_BATTLE, ZOOM_EXTENDED.ZOOM_STEPS: NEXT_BATTLE, ZOOM_EXTENDED.NO_FLASH_BANG: LIVE, ZOOM_EXTENDED.NO_SHOCK_WAVE: LIVE},
    BANKS_LOADER.NAME: {'*': RESTART},
    'driftkings': {'*': RESTART},  # selected configuration profile
}


def application_timing(component, field):
    if isinstance(field, (tuple, list)):
        field = '.'.join(str(part) for part in field)
    policy = APPLY_TIMING.get(component, {})
    # Specific child paths take precedence over a parent group and '*'.
    while field:
        if field in policy:
            return policy[field]
        field = field.rsplit('.', 1)[0] if '.' in field else ''
    return policy.get('*', RESTART)


def requires_restart(component, field):
    return application_timing(component, field) == RESTART
