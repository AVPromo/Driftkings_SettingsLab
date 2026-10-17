# -*- coding: utf-8 -*-
from Driftkings._constants import TECH_TREE_MARKS_OF_EXCELLENCE
from Driftkings.common import color_tables
from Driftkings.settings.controls_schema import control, slider, options
from Driftkings.settings.definitions.base import SectionDefinition


class TechTreeMarksOfExcellenceSettings(SectionDefinition):
    NAME = TECH_TREE_MARKS_OF_EXCELLENCE.NAME

    TRANSLATED_TITLE = True
    COLUMNS = (
        (
            options(TECH_TREE_MARKS_OF_EXCELLENCE.COLOR_RATING, [table['ScaleColor'] for table in color_tables]),
            control(TECH_TREE_MARKS_OF_EXCELLENCE.SHOW_IN_TECH_TREE),
            control(TECH_TREE_MARKS_OF_EXCELLENCE.SHOW_IN_TECH_TREE_MARK_OF_GUN_PERCENT),
            control(TECH_TREE_MARKS_OF_EXCELLENCE.SHOW_IN_TECH_TREE_MASTERY),
            control(TECH_TREE_MARKS_OF_EXCELLENCE.SHOW_IN_TECH_TREE_MARK_OF_GUN_TANK_NAME_COLORED),
        ),
        (
            slider(TECH_TREE_MARKS_OF_EXCELLENCE.BADGE_OFFSET_X, -300, 300, 1),
            slider(TECH_TREE_MARKS_OF_EXCELLENCE.BADGE_OFFSET_Y, -100, 100, 1),
        ),
    )
