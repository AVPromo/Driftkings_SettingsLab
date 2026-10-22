# -*- coding: utf-8 -*-
from driftkings._constants import AUTOAIM_TARGET_INDICATOR
from driftkings.settings.controls_schema import control
from driftkings.settings.definitions.base import SectionDefinition


class AutoaimTargetIndicatorSettings(SectionDefinition):
    NAME = AUTOAIM_TARGET_INDICATOR.NAME

    TRANSLATED_TITLE = True

    def normalize_loaded(self, values):
        for key in ('angle', 'catchHiddenTarget', 'disableArtyMode'):
            values.pop(key, None)
        return values

    def normalize_changes(self, values, changes):
        return self.normalize_loaded(values)

    def getControlColumns(self):
        return ((control(AUTOAIM_TARGET_INDICATOR.COLOR, 'ColorChoice'),), ())
