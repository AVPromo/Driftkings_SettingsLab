# -*- coding: utf-8 -*-
from Driftkings.common.utils.events import ModEvent
from Driftkings.common import callback

__all__ = ('populate',)

populate = ModEvent()


def delayed_hooks():
    global populate
    from Driftkings.common.utils import override
    from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
    populate = override(LobbyView, '_populate', populate)


callback(0, delayed_hooks)
