# -*- coding: utf-8 -*-
from collections import defaultdict
from functools import partial

from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator

from Driftkings._constants import BATTLE_ALIASES
from Driftkings._constants import GLOBAL, SIXTH_SENSE_ALERT
from Driftkings.common import getPlayer, square_position, sendChatMessage
from Driftkings.core.callbacks import callback
from Driftkings.core.hooks import override
from Driftkings.settings.service import settings_service
from Driftkings.settings.definitions.battle.sixth_sense_alert import SixthSenseAlertSettings as Settings
from Driftkings.views.battle.sixth_sense_alert import SixthSense

AS_BATTLE = BATTLE_ALIASES.SIXTH_SENSE_ALERT
config = Settings()


class MessagesSpotted(object):
    def __init__(self):
        self.macro = defaultdict(lambda: 'macros not found')
        self.__time = 0.5
        self.last_position = None

    def sendMessage(self):
        self.macro['pos'] = square_position.getSquarePosition()
        if self.macro['pos'] != self.last_position:
            message = settings_service.getComponentDict(config)[SIXTH_SENSE_ALERT.SPOTTED_TEXT] % self.macro
            if message:
                sendChatMessage(message, 1, settings_service.getComponentDict(config)[SIXTH_SENSE_ALERT.DELAY])
                self.last_position = self.macro['pos']

    def helpMessage(self):
        def message(avatar):
            avatar.guiSessionProvider.shared.chatCommands.handleChatCommand(BATTLE_CHAT_COMMAND_NAMES.SOS)
        if settings_service.getComponentDict(config)[SIXTH_SENSE_ALERT.HELP_MESSAGE]:
            callback(self.__time, partial(message, getPlayer()))


g_messages = MessagesSpotted()
g_view = None


@override(SixthSenseIndicator, '_sixthSenseToggle')
def new__sixthSenseToggle(func, self, isVisible, force):
    func(self, isVisible, force)
    # Never suppress the game's alert unless our replacement has loaded its icon.
    replacement = (g_view is not None and getattr(g_view, 'iconReady', False)
                   and settings_service.getComponentDict(config)[GLOBAL.ENABLED])
    self.flashObject.visible = not replacement
    if not isVisible:
        return
    player = getPlayer()
    if player and player.isVehicleAlive:
        if settings_service.getComponentDict(config)[GLOBAL.ENABLED]:
            if settings_service.getComponentDict(config)[SIXTH_SENSE_ALERT.SPOTTED_MESSAGE]:
                g_messages.sendMessage()
            if settings_service.getComponentDict(config)[SIXTH_SENSE_ALERT.HELP_MESSAGE]:
                g_messages.helpMessage()




def getBattleViews():
    return ((AS_BATTLE, SixthSense, config),)
