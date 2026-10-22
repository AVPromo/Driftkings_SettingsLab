# -*- coding: utf-8 -*-
from driftkings._constants import AIMING_COUNTDOWN, GLOBAL
from driftkings.settings.controls_schema import color, control, slider
from driftkings.settings.definitions.base import SectionDefinition


class AimingCountdownSettings(SectionDefinition):
    NAME = AIMING_COUNTDOWN.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        colorLabelRed = color(AIMING_COUNTDOWN.RED, 'colorRed')
        colorLabelOrange = color(AIMING_COUNTDOWN.ORANGE, 'colorOrange')
        colorLabelYellow = color(AIMING_COUNTDOWN.YELLOW, 'colorYellow')
        colorLabelGreen = color(AIMING_COUNTDOWN.GREEN, 'colorGreen')
        colorLabelBlue = color(AIMING_COUNTDOWN.BLUE, 'colorBlue')
        colorLabelPurple = color(AIMING_COUNTDOWN.PURPLE, 'colorPurple')
        return (
            [
                colorLabelRed,
                colorLabelOrange,
                colorLabelYellow,
                colorLabelGreen,
                colorLabelBlue,
                colorLabelPurple
            ],
            [
                control(AIMING_COUNTDOWN.TEMPLATE, 'TextInput', 400),
                slider(GLOBAL.X, -2000, 2000, 1, '{{value}}%s' % ' X'),
                slider(GLOBAL.Y, -2000, 2000, 1, '{{value}}%s' % ' Y')
            ]
        )
