# -*- coding: utf-8 -*-
from Driftkings._constants import SERVER_TURRET_SYNC
from Driftkings.settings.controls_schema import control
from Driftkings.settings.definitions.base import SectionDefinition


class ServerTurretSyncSettings(SectionDefinition):
    NAME = SERVER_TURRET_SYNC.NAME

    TRANSLATED_TITLE = True
    COLUMNS = ((control(SERVER_TURRET_SYNC.SERVER_TURRET),
                control(SERVER_TURRET_SYNC.ACTIVATE_MESSAGE)), ())

    def normalize_loaded(self, values):
        for key in ('fixAccuracyInMove', 'fixWheelCruiseControl', 'autoActivateWheelMode',
                    'maxWheelMode', 'buttonAutoMode', 'buttonMaxMode'):
            values.pop(key, None)
        return values
