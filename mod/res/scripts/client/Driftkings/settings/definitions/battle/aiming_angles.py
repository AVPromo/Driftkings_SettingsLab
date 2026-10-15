# -*- coding: utf-8 -*-
from Driftkings._constants import AIMING_ANGLES
from Driftkings.settings.controls_schema import options
from Driftkings.settings.definitions.base import SectionDefinition


class AimingAnglesSettings(SectionDefinition):
    NAME = AIMING_ANGLES.NAME

    TRANSLATED_TITLE = False

    def getControlColumns(self):
        return (
            [
                options(AIMING_ANGLES.HORIZONTAL, [self.i18n['UI_setting_horizontal_%s' % i] for i in xrange(7)], 'RadioButtonGroup')
            ],
            [
                options(AIMING_ANGLES.VERTICAL, [self.i18n['UI_setting_vertical_%s' % i] for i in xrange(7)], 'RadioButtonGroup')
            ]
        )
