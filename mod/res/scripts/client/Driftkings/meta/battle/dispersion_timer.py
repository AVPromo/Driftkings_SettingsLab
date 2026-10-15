# -*- coding: utf-8 -*-
from Driftkings.meta.battle.base import CrosshairMeta


class DispersionTimerMeta(CrosshairMeta):
    FLASH_CLASS = 'driftkings.battle.components.dispersion_timer.DispersionTimerUI'

    def as_updateTimerTextS(self, text):
        return self._sendChanged('as_updateTimerText', text)
