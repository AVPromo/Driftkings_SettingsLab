# -*- coding: utf-8 -*-
import BigWorld

from Driftkings.common.utils import events
from Driftkings.common.utils.abstract import *
from Driftkings.common.utils.chat import *
from Driftkings.common.utils.colorRatting import *
from Driftkings.common.utils.game import *
from Driftkings.common.utils.iter import *
from Driftkings.common.utils.logger import *
from Driftkings.common.utils.monkeypatch import *
from Driftkings.common.utils.wgUtils import *


def _publish_delayed_aliases(delayed, modules, root):
    canonical = 'Driftkings.common.utils.delayed'
    compatibility = 'Driftkings.common.delayed'
    suffixes = ('', 'api', 'utils', 'utils.dialogs',
                'utils.notifications_hooks', 'utils.old_dialogs')
    mappings = []
    attributes = [(root, 'delayed', delayed),
                  (modules[__name__], 'delayed', delayed)]
    for suffix in suffixes:
        physical = canonical + ('.' + suffix if suffix else '')
        alias = compatibility + ('.' + suffix if suffix else '')
        target = modules.get(physical)
        if (not isinstance(target, type(delayed)) or target.__name__ != physical
                or (not suffix and target is not delayed)):
            logError(__name__, 'Delayed alias publication aborted: {0} -> {1}; canonical module missing or invalid. Restart the client.', alias, physical)
            return False
        if alias in modules and modules[alias] is not target:
            logError(__name__, 'Delayed alias publication aborted: {0} -> {1}; divergent module already loaded. Restart the client.', alias, physical)
            return False
        mappings.append((alias, target))
        if suffix:
            parent_path, attribute = physical.rsplit('.', 1)
            parent = modules.get(parent_path)
            if parent is None:
                logError(__name__, 'Delayed alias publication aborted: {0} -> {1}; canonical parent missing. Restart the client.', alias, physical)
                return False
            attributes.append((parent, attribute, target))
    for parent, attribute, target in attributes:
        if hasattr(parent, attribute) and getattr(parent, attribute) is not target:
            logError(__name__, 'Delayed alias publication aborted: {0} -> {1}; divergent parent attribute {2}.{3}. Restart the client.',
                     compatibility + target.__name__[len(canonical):], target.__name__, parent.__name__, attribute)
            return False
    for alias, target in mappings:
        modules[alias] = target
    for parent, attribute, target in attributes:
        setattr(parent, attribute, target)
    return True


def __import_delayed():
    from Driftkings.common.utils import delayed
    import Driftkings.common
    import sys
    _publish_delayed_aliases(delayed, sys.modules, Driftkings.common)


def initializeDelayedImports():
    # Called by the root package after its public functions are available.
    BigWorld.callback(0, __import_delayed)
