# -*- coding: utf-8 -*-
# Keep our package search path independent of facade imports in the client.
_package_path = list(__path__)
from Driftkings import VERSION
__CORE_NAME__ = 'Driftkings.common'

import sys
import time
import traceback

import ResMgr

from Driftkings.common.config import *
__path__ = list(_package_path)
from Driftkings.common.utils import *
__path__ = list(_package_path)

curCV = ResMgr.openSection('../paths.xml')['Paths'].values()[0].asString

# Resolve the definition-only helper while the package body is being imported.
from importlib import import_module as _import_module
try:
    _bootstrap = _import_module('Driftkings.common.bootstrap')
except ImportError:
    logError(__CORE_NAME__, 'Bootstrap resolution failed: package={0}; path={1}; resource={2}',
             globals().get('__package__'), globals().get('__path__'),
             ResMgr.openSection('scripts/client/Driftkings/common/bootstrap.pyc') is not None)
    raise


def initializeCore():
    return _bootstrap.initializeCore(globals())


def logStartupInfo():
    return _bootstrap.logStartupInfo(globals())


def initializeSubsystems():
    return _bootstrap.initializeSubsystems(globals())


# Initialize the core when the module is imported
initializeCore()
# Keep the implementation module out of the root implicit wildcard surface.
globals().pop('bootstrap', None)
initializeDelayedImports()
