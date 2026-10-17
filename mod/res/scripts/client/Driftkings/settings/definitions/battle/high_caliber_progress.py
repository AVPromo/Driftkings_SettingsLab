# -*- coding: utf-8 -*-
from Driftkings._constants import HIGH_CALIBER_PROGRESS
from Driftkings.settings.controls_schema import control
from Driftkings.settings.definitions.base import SectionDefinition


class HighCaliberProgressSettings(SectionDefinition):
    NAME = HIGH_CALIBER_PROGRESS.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            control(HIGH_CALIBER_PROGRESS.BACK_GROUND_ENABLED),
            control(HIGH_CALIBER_PROGRESS.TEXT_LOCK),
        ),
        (
        ),
    )
