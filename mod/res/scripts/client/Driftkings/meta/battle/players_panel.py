# -*- coding: utf-8 -*-
from Driftkings.meta.battle.base import ComponentMeta
from Driftkings.core.diagnostics import diagnostics


class PlayersPanelMeta(ComponentMeta):
    FLASH_CLASS = 'driftkings.battle.components.ratings.RatingScreens'

    def as_setRosterS(self, payload):
        if self._isDAAPIInited():
            if diagnostics.enabled:
                return diagnostics.call('flash.ratings.roster', self.flashObject.as_setRoster, payload)
            return self.flashObject.as_setRoster(payload)

    def reportState(self, state):
        raise NotImplementedError

    def hoverPanel(self, expanded):
        raise NotImplementedError

    def reportWidths(self, left, right):
        raise NotImplementedError

    def reportScreens(self, panel, loading, tab):
        raise NotImplementedError

    def reportPerformance(self, message):
        raise NotImplementedError
