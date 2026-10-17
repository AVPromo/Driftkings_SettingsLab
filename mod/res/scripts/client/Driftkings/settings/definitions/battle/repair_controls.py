# -*- coding: utf-8 -*-
from Driftkings._constants import REPAIR_CONTROLS
from Driftkings.settings.controls_schema import control, hotkey
from Driftkings.settings.definitions.base import SectionDefinition


class RepairControlsSettings(SectionDefinition):
    NAME = REPAIR_CONTROLS.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        return (
            [
                hotkey(REPAIR_CONTROLS.BUTTON_CHASSIS),
                hotkey(REPAIR_CONTROLS.BUTTON_REPAIR),
                control(REPAIR_CONTROLS.USE_GOLD_KITS)
            ],
            [
                control(REPAIR_CONTROLS.RESTORE_CHASSIS),
                control(REPAIR_CONTROLS.REMOVE_STUN),
                control(REPAIR_CONTROLS.EXTINGUISH_FIRE),
                control(REPAIR_CONTROLS.HEAL_CREW),
                control(REPAIR_CONTROLS.REPAIR_DEVICES)
            ]
        )

    def normalize_loaded(self, values):
        for key in ('autoRepair', 'timerMin', 'timerMax'):
            values.pop(key, None)
        return values

    def normalize_changes(self, values, changes):
        return self.normalize_loaded(values)
