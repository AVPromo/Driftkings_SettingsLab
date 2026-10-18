# -*- coding: utf-8 -*-
from Driftkings._constants import HANGAR_PREFERENCES
from Driftkings.settings.controls_schema import control, slider
from Driftkings.settings.definitions.base import SectionDefinition


class HangarPreferencesSettings(SectionDefinition):
    NAME = HANGAR_PREFERENCES.NAME

    TRANSLATED_TITLE = True

    def normalize_loaded(self, values):
        # Retired presets; retain personal clock text and position.
        for key in ('clockStyle', 'clockSeconds', 'clock24Hour', 'customClockFormat', 'text', 'panel'):
            values.pop(key, None)
        return values

    def getControlColumns(self):
        return (
            [
                control(HANGAR_PREFERENCES.AUTO_LOGIN),
                control(HANGAR_PREFERENCES.CLOCK),
                control(HANGAR_PREFERENCES.CLOCK_BACKGROUND),
                slider(HANGAR_PREFERENCES.CLOCK_X, -3840, 3840, 1),
                slider(HANGAR_PREFERENCES.CLOCK_Y, -2160, 2160, 1),
                slider(HANGAR_PREFERENCES.CLOCK_SCALE, 50, 200, 5),
                control(HANGAR_PREFERENCES.CUSTOM_CLOCK_TEXT, 'TextArea'),
                control(HANGAR_PREFERENCES.ALLOW_EXCHANGE_XPIN_TECH_TREE),
                control(HANGAR_PREFERENCES.ALLOW_CHANNEL_BUTTON_BLINKING),
                control(HANGAR_PREFERENCES.SHOW_XP_TO_UNLOCK_VEH),
                control(HANGAR_PREFERENCES.BLOCK_VEHICLE_IF_LOW_AMMO),
                slider(HANGAR_PREFERENCES.LOW_AMMO_PERCENTAGE, 0, 100, 1, '{{value}}%'),
                control(HANGAR_PREFERENCES.SHOW_BATTLE_COUNT),
                control(HANGAR_PREFERENCES.SHOW_BUTTON),
                control(HANGAR_PREFERENCES.SHOW_GENERAL_CHAT_BUTTON),
                control(HANGAR_PREFERENCES.SHOW_POP_UP_MESSAGES),
                control(HANGAR_PREFERENCES.LOOT_BOXES_WIDGET),
                control(HANGAR_PREFERENCES.SHOW_DAILY_QUEST_WIDGET),
                control(HANGAR_PREFERENCES.SHOW_EVENT_BANNER),
                control(HANGAR_PREFERENCES.SHOW_EVENT_TOURNAMENT_WIDGET),
                control(HANGAR_PREFERENCES.SHOW_PROGRESSIVE_DECALS_WINDOW),
                control(HANGAR_PREFERENCES.SHOW_BATTLE_PASS_WIDGET)
            ],
            [
                control(HANGAR_PREFERENCES.SHOW_PROMO_PREM_VEHICLE),
                control(HANGAR_PREFERENCES.SHOW_UNREAD_COUNTER),
                control(HANGAR_PREFERENCES.SHOW_BUTTON_COUNTERS),
                control(HANGAR_PREFERENCES.HIDE_BTN_COUNTERS),
                control(HANGAR_PREFERENCES.SHOW_RANKED_BATTLE_RESULTS),
                control(HANGAR_PREFERENCES.SHOW_HANGAR_PRESTIGE_WIDGET),
                control(HANGAR_PREFERENCES.SHOW_PROFILE_PRESTIGE_WIDGET),
                control(HANGAR_PREFERENCES.SHOW_ACHIEVEMENT_POPUPS),
                control(HANGAR_PREFERENCES.SHOW_ACHIEVEMENT_REWARD_WINDOW),
                control(HANGAR_PREFERENCES.FIELD_MAIL),
                control('showBuyPremiumButton'),
                control('showPremiumShopButton'),
                control('showReferralButton'),
                control('showWotPlusButton'),
                control('premiumTime'),
            ]
        )
