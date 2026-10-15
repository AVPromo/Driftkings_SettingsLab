# -*- coding: utf-8 -*-
from Driftkings._constants import SAFE_SHOT
from Driftkings.settings.controls_schema import control, slider, hotkey
from Driftkings.settings.definitions.base import SectionDefinition


class SafeShotSettings(SectionDefinition):
    NAME = SAFE_SHOT.NAME

    TRANSLATED_TITLE = False
    COLUMNS = (
        (
            control(SAFE_SHOT.WASTE_SHOT_BLOCK),
            control(SAFE_SHOT.TEAM_SHOT_BLOCK),
            control(SAFE_SHOT.TEAM_KILLER_SHOT_UNBLOCK),
            control(SAFE_SHOT.DEAD_SHOT_BLOCK),
            control(SAFE_SHOT.ACTIVATE_MESSAGE),
        ),
        (
            control(SAFE_SHOT.TRIGGER_MESSAGE),
            hotkey(SAFE_SHOT.DISABLE_KEY),
            control(SAFE_SHOT.CHAT_MESSAGES, 'TextInput', 350),
            slider(SAFE_SHOT.DEAD_SHOT_BLOCK_TIME_OUT, 2, 10, 1, '{{value}}%s' % '.sec'),
        ),
    )
