# -*- coding: utf-8 -*-
"""Explicit common facade; retain its public API and independent package path."""
_package_path = list(__path__)
from Driftkings import VERSION

import ResMgr

from Driftkings.common.config import loadJson, smart_update
__path__ = list(_package_path)
from Driftkings.common.utils import (
    BigWorld, events, redirect_traceback, sendChatMessage,
    color_tables, getRatingColors, getColor, getStatisticColor,
    getRatingPaletteColor, getComparisonColor, getMoeDamageColor, BigWorld_callback,
    sendPanelMessage, checkKeys, refreshCurrentVehicle, Sound,
    remDups, logDebug, logInfo, logError,
    logWarning, logException, override, overrideMethod,
    overrideStaticMethod, overrideClassMethod, find_attr, find_attr_name,
    battle_pages, battle_range, callback, cancelCallback,
    checkNamesList, distanceToEntityVehicle, getAccountDBID, getDistanceTo,
    getEntity, getPercent, getPlayer, getTarget,
    getVehCD, hexToDecimal, isReplay, percentToRgb,
    replaceMacros, serverTime, square_position, xvmInstalled,
    abstract, chat, colorRatting, game,
    iter, logger, monkeypatch, wgUtils,
)
__path__ = list(_package_path)

curCV = ResMgr.openSection('../paths.xml')['Paths'].values()[0].asString
