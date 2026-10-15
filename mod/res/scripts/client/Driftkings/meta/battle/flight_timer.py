# -*- coding: utf-8 -*-
from Driftkings.meta.battle.base import CrosshairMeta


class FlightTimeMeta(CrosshairMeta):
    FLASH_CLASS = 'driftkings.battle.components.flight_timer.FlightTimerUI'

    def as_flightTimeS(self, text):
        return self._sendChanged('as_flightTime', text)
