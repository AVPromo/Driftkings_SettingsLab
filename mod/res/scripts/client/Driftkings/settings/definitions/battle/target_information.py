# -*- coding: utf-8 -*-
from Driftkings._constants import TARGET_INFORMATION
from Driftkings.settings.controls_schema import control, hotkey, options, slider
from Driftkings.settings.definitions.base import SectionDefinition


class TargetInformationSettings(SectionDefinition):
    NAME = TARGET_INFORMATION.NAME

    TRANSLATED_TITLE = True

    def getControlColumns(self):
        xFormat = self.i18n['UI_delay_format']
        showForOptions = ['all', 'ally', 'enemy']
        showForLabels = [self.i18n['UI_showFor_' + x] for x in showForOptions]
        templateOptions = ['default', 'minimal', 'detailed', 'full', 'kmp', 'ndo', 'driftkings']
        templateLabels = [self.i18n['UI_templatePreset_' + x] for x in templateOptions]
        return (
            [
                control(TARGET_INFORMATION.TEXT_LOCK),
                slider(TARGET_INFORMATION.DELAY, 1.0, 10, 1.0, '{{value}}%s' % xFormat),
                control(TARGET_INFORMATION.ALIVE_ONLY),
                hotkey(TARGET_INFORMATION.ALT_KEY),
                options(TARGET_INFORMATION.SHOW_FOR, showForLabels)
            ],
            [
                control(TARGET_INFORMATION.BACKGROUND_ENABLED),
                slider(TARGET_INFORMATION.BACKGROUND_ALPHA, 0.0, 1.0, 0.1, '{{value}}'),
                options(TARGET_INFORMATION.TEMPLATE_PRESET, templateLabels)
            ]
        )
