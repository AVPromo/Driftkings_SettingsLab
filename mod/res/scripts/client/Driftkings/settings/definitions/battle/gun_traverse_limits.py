# -*- coding: utf-8 -*-
from Driftkings._constants import GUN_TRAVERSE_LIMITS
from Driftkings.settings.controls_schema import options
from Driftkings.settings.definitions.base import SectionDefinition


class GunTraverseLimitsSettings(SectionDefinition):
    NAME = GUN_TRAVERSE_LIMITS.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        return (
            [
                options(GUN_TRAVERSE_LIMITS.HORIZONTAL, [self.i18n['UI_setting_horizontal_%s' % i] for i in xrange(7)], 'RadioButtonGroup')
            ],
            [
                options(GUN_TRAVERSE_LIMITS.VERTICAL, [self.i18n['UI_setting_vertical_%s' % i] for i in xrange(7)], 'RadioButtonGroup')
            ]
        )
