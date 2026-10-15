# -*- coding: utf-8 -*-
from Driftkings._constants import BANKS_LOADER
from Driftkings.settings.definitions.base import SectionDefinition


class BanksLoaderSettings(SectionDefinition):
    NAME = BANKS_LOADER.NAME

    AUTOMATIC_CONTROLS = True
