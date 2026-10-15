# -*- coding: utf-8 -*-
"""Canonical section names and read-only compatibility with previous releases."""
import re

LEGACY_NAMES = {'AccountManager': 'account_manager',
 'AimingAngles': 'aiming_angles',
 'ArcadeZoom': 'arcade_zoom',
 'ArmorCalculator': 'armor_calculator',
 'ArtySplash': 'arty_splash',
 'AutoAimOptimize': 'auto_aim_optimize',
 'AutoClaimClan': 'auto_claim_clan',
 'BanksLoader': 'banks_loader',
 'BattleEfficiency': 'battle_efficiency',
 'BattleOptions': 'battle_options',
 'BattleStat': 'battle_stat',
 'CarouselStats': 'carousel_stats',
 'CrewSettings': 'crew_settings',
 'DispersionCircle': 'dispersion_circle',
 'DispersionTimer': 'dispersion_timer',
 'DistanceMarker': 'distance_marker',
 'Driftkings': 'driftkings',
 'FlightTimer': 'flight_timer',
 'HangarOptions': 'hangar_options',
 'InfoPanel': 'info_panel',
 'LogsSwapper': 'logs_swapper',
 'MainGun': 'main_gun',
 'MarksOnGunBattle': 'marks_on_gun_battle',
 'MarksOnGunHangar': 'marks_on_gun_hangar',
 'MarksOnGunTechTree': 'marks_on_gun_tech_tree',
 'MinimapPlugins': 'minimap_plugins',
 'OwnHealth': 'own_health',
 'PlayerPanelPro': 'player_panel_pro',
 'RepairExtended': 'repair_extended',
 'SafeShot': 'safe_shot',
 'ServerTurretExtended': 'server_turret_extended',
 'SixthSense': 'sixth_sense',
 'SpottedExtendedLight': 'spotted_extended_light',
 'Stats': 'stats',
 'ZoomExtended': 'zoom_extended'}
SECTIONS = tuple(sorted(name for old, name in LEGACY_NAMES.items() if old not in ('Driftkings', 'Stats')))
PREVIOUS_NAMES = dict((name, old) for old, name in LEGACY_NAMES.items())

def section_name(value):
    name = value.NAME if hasattr(value, "NAME") else value
    name = LEGACY_NAMES.get(name, name)
    if not isinstance(name, (str, type(u""))) or not re.match(r"^[a-z][a-z0-9_]*\Z", name):
        raise ValueError("Invalid settings section: " + str(name))
    return name

def previous_name(value):
    name = section_name(value)
    return PREVIOUS_NAMES.get(name, name)
