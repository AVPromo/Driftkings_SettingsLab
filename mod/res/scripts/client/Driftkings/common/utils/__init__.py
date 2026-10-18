# -*- coding: utf-8 -*-
"""Explicit shared utility exports; import order preserves client initialization."""
import BigWorld

from Driftkings.common.utils import events
from Driftkings.common.utils.abstract import (
    redirect_traceback,
)
from Driftkings.common.utils.chat import (
    sendChatMessage,
)
from Driftkings.common.utils.colorRatting import (
    color_tables, getRatingColors, getColor, getStatisticColor,
    getRatingPaletteColor, getComparisonColor, getMoeDamageColor,
)
from Driftkings.common.utils.game import (
    BigWorld_callback, sendPanelMessage, checkKeys, refreshCurrentVehicle,
    Sound,
)
from Driftkings.common.utils.iter import (
    remDups,
)
from Driftkings.common.utils.logger import (
    logDebug, logInfo, logError, logWarning,
    logException,
)
from Driftkings.common.utils.monkeypatch import (
    override, overrideMethod, overrideStaticMethod, overrideClassMethod,
    find_attr, find_attr_name,
)
from Driftkings.common.utils.wgUtils import (
    battle_pages, battle_range, callback, cancelCallback,
    checkNamesList, distanceToEntityVehicle, getAccountDBID, getColor,
    getDistanceTo, getEntity, getPercent, getPlayer,
    getTarget, getVehCD, hexToDecimal, isReplay,
    percentToRgb, replaceMacros, serverTime, square_position,
    xvmInstalled,
)

from Driftkings.common.utils import (
    abstract, chat, colorRatting, game,
    iter, logger, monkeypatch, wgUtils,
)

__all__ = (
    'BigWorld', 'events', 'redirect_traceback', 'sendChatMessage',
    'color_tables', 'getRatingColors', 'getColor', 'getStatisticColor',
    'getRatingPaletteColor', 'getComparisonColor', 'getMoeDamageColor', 'BigWorld_callback',
    'sendPanelMessage', 'checkKeys', 'refreshCurrentVehicle', 'Sound',
    'remDups', 'logDebug', 'logInfo', 'logError',
    'logWarning', 'logException', 'override', 'overrideMethod',
    'overrideStaticMethod', 'overrideClassMethod', 'find_attr', 'find_attr_name',
    'battle_pages', 'battle_range', 'callback', 'cancelCallback',
    'checkNamesList', 'distanceToEntityVehicle', 'getAccountDBID', 'getDistanceTo',
    'getEntity', 'getPercent', 'getPlayer', 'getTarget',
    'getVehCD', 'hexToDecimal', 'isReplay', 'percentToRgb',
    'replaceMacros', 'serverTime', 'square_position', 'xvmInstalled',
    'abstract', 'chat', 'colorRatting', 'game',
    'iter', 'logger', 'monkeypatch', 'wgUtils',
)
