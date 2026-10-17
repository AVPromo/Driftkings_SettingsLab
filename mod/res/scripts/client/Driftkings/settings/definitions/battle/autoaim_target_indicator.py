# -*- coding: utf-8 -*-
from Driftkings._constants import AUTOAIM_TARGET_INDICATOR
from Driftkings.settings.definitions.base import SectionDefinition


class AutoaimTargetIndicatorSettings(SectionDefinition):
    NAME = AUTOAIM_TARGET_INDICATOR.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        # Preserve old config keys, but do not expose discontinued acquisition.
        # The existing enabled switch now controls the native-target box.
        return ((), ())
