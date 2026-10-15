# -*- coding: utf-8 -*-
from Driftkings._constants import CREW_SETTINGS
from Driftkings.settings.controls_schema import control, slider
from Driftkings.settings.definitions.base import SectionDefinition


class CrewSettingsSettings(SectionDefinition):
    NAME = CREW_SETTINGS.NAME

    TRANSLATED_TITLE = True
    COLUMNS = ((control(CREW_SETTINGS.CREW_AUTO_RETURN), control(CREW_SETTINGS.CREW_RETURN_BY_DEFAULT), slider(CREW_SETTINGS.AUTO_RETURN_DELAY, 0.5, 5.0, 0.5), control(CREW_SETTINGS.SHOW_NOTIFICATIONS),), (control(CREW_SETTINGS.EXCLUDE_PREMIUM_VEHICLES),),)
