# -*- coding: utf-8 -*-
from Driftkings._constants import ACCOUNT_MANAGER
from Driftkings.settings.definitions.base import SectionDefinition


class AccountManagerSettings(SectionDefinition):
    NAME = ACCOUNT_MANAGER.NAME

    AUTOMATIC_CONTROLS = True
