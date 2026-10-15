# -*- coding: utf-8 -*-
from Driftkings._constants import AUTO_AIM_OPTIMIZE
from Driftkings.settings.templates.base import ComponentSettings


class AutoAimOptimizeSettings(ComponentSettings):
    COMPONENT = AUTO_AIM_OPTIMIZE.ID

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        # Preserve old config keys, but do not expose discontinued acquisition.
        # The existing enabled switch now controls the native-target box.
        return ((), ())
