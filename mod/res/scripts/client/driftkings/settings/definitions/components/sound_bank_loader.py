# -*- coding: utf-8 -*-
from driftkings._constants import SOUND_BANK_LOADER
from driftkings.settings.definitions.base import SectionDefinition


class SoundBankLoaderSettings(SectionDefinition):
    NAME = SOUND_BANK_LOADER.NAME

    AUTOMATIC_CONTROLS = True
