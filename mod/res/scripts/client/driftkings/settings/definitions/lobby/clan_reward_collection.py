# -*- coding: utf-8 -*-
from driftkings._constants import CLAN_REWARD_COLLECTION
from driftkings.settings.definitions.base import SectionDefinition


class ClanRewardCollectionSettings(SectionDefinition):
    NAME = CLAN_REWARD_COLLECTION.NAME

    TRANSLATED_TITLE = True
    COLUMNS = ((),(),)
