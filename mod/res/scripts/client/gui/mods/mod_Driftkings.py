# -*- coding: utf-8 -*-
"""Single game entry point; Core owns the application lifecycle."""
import logging

try:
    from realm import CURRENT_REALM
except ImportError:
    CURRENT_REALM = None

_core = None
if CURRENT_REALM in ('EU', 'NA', 'ASIA'):
    from Driftkings.core import Core
    _core = Core()
else:
    logging.getLogger('Driftkings.Loader').warning('Unsupported client realm: %s; Driftkings disabled', CURRENT_REALM)


def init():
    if _core is not None:
        _core.start()


def fini():
    if _core is not None:
        _core.stop()
