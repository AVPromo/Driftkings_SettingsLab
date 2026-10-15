# -*- coding: utf-8 -*-
from Driftkings.common.utils.events import ModEvent
from Driftkings.common import callback

__all__ = ('fini',)

fini = ModEvent()


def delayed_hooks():
    global fini
    from gui.app_loader.loader import AppLoader
    from Driftkings.common.utils import override
    fini = override(AppLoader, 'fini', fini)


callback(0, delayed_hooks)
