# -*- coding: utf-8 -*-
from Driftkings._constants import GLOBAL, OWN_HEALTH
from Driftkings.settings.controls_schema import slider
from Driftkings.settings.definitions.base import SectionDefinition


class OwnHealthSettings(SectionDefinition):
    NAME = OWN_HEALTH.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            slider(GLOBAL.X, -2000, 2000, 1, '{{value}}%s' % ' px'),
            slider(GLOBAL.Y, -2000, 2000, 1, '{{value}}%s' % ' px'),
        ),
        (
        ),
    )
