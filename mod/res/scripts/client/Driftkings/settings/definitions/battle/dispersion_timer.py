# -*- coding: utf-8 -*-
from Driftkings._constants import DISPERSION_TIMER, GLOBAL
from Driftkings.settings.controls_schema import color, control, slider
from Driftkings.settings.definitions.base import SectionDefinition


class DispersionTimerSettings(SectionDefinition):
    NAME = DISPERSION_TIMER.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        colorLabelRed = color(DISPERSION_TIMER.RED, 'colorRed')
        colorLabelOrange = color(DISPERSION_TIMER.ORANGE, 'colorOrange')
        colorLabelYellow = color(DISPERSION_TIMER.YELLOW, 'colorYellow')
        colorLabelGreen = color(DISPERSION_TIMER.GREEN, 'colorGreen')
        colorLabelBlue = color(DISPERSION_TIMER.BLUE, 'colorBlue')
        colorLabelPurple = color(DISPERSION_TIMER.PURPLE, 'colorPurple')
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
                control(DISPERSION_TIMER.TEMPLATE, 'TextInput', 400),
                slider(GLOBAL.X, -2000, 2000, 1, '{{value}}%s' % ' X'),
                slider(GLOBAL.Y, -2000, 2000, 1, '{{value}}%s' % ' Y')
            ]
        )
