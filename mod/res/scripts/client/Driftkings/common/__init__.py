# -*- coding: utf-8 -*-
# Keep our package search path independent of facade imports in the client.
_package_path = list(__path__)
from Driftkings import VERSION

import ResMgr

from Driftkings.common.config import *
__path__ = list(_package_path)
from Driftkings.common.utils import *
__path__ = list(_package_path)

curCV = ResMgr.openSection('../paths.xml')['Paths'].values()[0].asString
