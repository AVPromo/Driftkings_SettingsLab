# -*- coding: utf-8 -*-
from Driftkings._constants import AUTO_AIM_OPTIMIZE
from Driftkings.settings.definitions.base import SectionDefinition


class AutoAimOptimizeSettings(SectionDefinition):
    NAME = AUTO_AIM_OPTIMIZE.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        # Preserve old config keys, but do not expose discontinued acquisition.
        # The existing enabled switch now controls the native-target box.
        return ((), ())
