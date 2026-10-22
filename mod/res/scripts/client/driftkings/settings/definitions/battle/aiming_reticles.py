# -*- coding: utf-8 -*-
from driftkings._constants import AIMING_RETICLES
from driftkings.settings.controls_schema import control, options, slider
from driftkings.settings.definitions.base import SectionDefinition


class AimingReticlesSettings(SectionDefinition):
    NAME = AIMING_RETICLES.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        from gui.Scaleform.locale.SETTINGS import SETTINGS
        from helpers import i18n
        CUSTOM_AIMING_CIRCLE_SHAPE_OPTIONS = [
            i18n.makeString(SETTINGS.AIM_MIXING_TYPE0),
            i18n.makeString(SETTINGS.AIM_MIXING_TYPE1),
            i18n.makeString(SETTINGS.AIM_MIXING_TYPE2),
            i18n.makeString(SETTINGS.AIM_MIXING_TYPE3)
        ]
        CUSTOM_CROSSHAIR_SHAPE_OPTIONS = [
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE0),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE1),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE2),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE3),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE4),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE5),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE6),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE7),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE8),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE9),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE10),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE11),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE12),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE13),
            i18n.makeString(SETTINGS.AIM_GUNTAG_TYPE14)
        ]
        return (
            [
                control(AIMING_RETICLES.SHOW_CLIENT_AND_SERVER_RETICLE_BETA),
                control(AIMING_RETICLES.SHOW_SERVER_SPG_STRATEGIC_RETICLE)
            ],
            [
                slider(AIMING_RETICLES.GUN_MARKER_MINIMUM_SIZE, 0, 32, 1, '{{value}}px'),
                slider(AIMING_RETICLES.PERCENT_CORRECTION, 0, 100, 1, '{{value}}%'),
                options(AIMING_RETICLES.SERVER_RETICLE_AIMING_CIRCLE_SHAPE, CUSTOM_AIMING_CIRCLE_SHAPE_OPTIONS),
                slider(AIMING_RETICLES.SERVER_RETICLE_AIMING_CIRCLE_OPACITY, 0, 100, 1, '{{value}}%'),
                options(AIMING_RETICLES.SERVER_RETICLE_GUN_MARKER_SHAPE, CUSTOM_CROSSHAIR_SHAPE_OPTIONS),
                slider(AIMING_RETICLES.SERVER_RETICLE_GUN_MARKER_OPACITY, 0, 100, 1, '{{value}}%')
            ]
        )
