# -*- coding: utf-8 -*-
from Event import SafeEvent, EventManager

_manager = EventManager()


class _EventWrapper(object):
    def __init__(self):
        self.event = SafeEvent(_manager)

    def __call__(self, handler):
        self.event += handler
        return handler


class ModEvent(object):
    def __init__(self):
        self.before = _EventWrapper()
        self.after = _EventWrapper()
        self._final = _EventWrapper()

    def __call__(self, func, *args, **kwargs):
        self.before.event(*args, **kwargs)
        result = func(*args, **kwargs)
        self.after.event(*args, **kwargs)
        self._final.event(*args, **kwargs)
        return result


from Driftkings.common.utils.events import game, player_avatar, lobby_view, login_view
PlayerAvatar, LobbyView, LoginView = player_avatar, lobby_view, login_view


@game.fini._final
def fini(*_, **__):
    _manager.clear()
