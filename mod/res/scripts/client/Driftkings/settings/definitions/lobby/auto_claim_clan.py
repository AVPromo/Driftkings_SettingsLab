# -*- coding: utf-8 -*-
from Driftkings._constants import AUTO_CLAIM_CLAN
from Driftkings.settings.definitions.base import SectionDefinition


class AutoClaimClanSettings(SectionDefinition):
    NAME = AUTO_CLAIM_CLAN.NAME

    TRANSLATED_TITLE = True
    COLUMNS = ((),(),)
