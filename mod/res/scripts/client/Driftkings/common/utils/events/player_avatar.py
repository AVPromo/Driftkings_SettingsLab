# -*- coding: utf-8 -*-
from Driftkings.common.utils.events import ModEvent
from Driftkings.common import callback

__all__ = ('startGUI', 'destroyGUI')

startGUI = ModEvent()
destroyGUI = ModEvent()


def delayed_hooks():
    global startGUI, destroyGUI
    from Avatar import PlayerAvatar
    from Driftkings.common.utils import override
    startGUI = override(PlayerAvatar, '__startGUI', startGUI)
    destroyGUI = override(PlayerAvatar, '__destroyGUI', destroyGUI)


callback(0, delayed_hooks)
