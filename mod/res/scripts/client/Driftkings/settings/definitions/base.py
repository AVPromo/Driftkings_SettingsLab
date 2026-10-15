# -*- coding: utf-8 -*-
"""Section declarations: presentation and feature-specific normalization only."""
from Driftkings.settings.settings_data import defaults, default_keys
from Driftkings.settings.hotkeys import processHotKeys


class SectionDefinition(object):
    NAME = None
    TRANSLATED_TITLE = True
    COLUMNS = ((), ())
    AUTOMATIC_CONTROLS = False
    STORAGE_CLASS = None
    STORAGE_FILES = None

    def __init__(self):
        from Driftkings.settings.service import settings_service
        settings_service.initialize(self)

    def getControlColumns(self):
        return self.COLUMNS

    def getSettingsDefaults(self):
        values = defaults(self.NAME)
        processHotKeys(values, default_keys(self.NAME), 'read')
        return self.normalize_loaded(values)

    def normalize_loaded(self, values):
        return values

    def normalize_changes(self, values, changes):
        return values

    def loadLang(self):
        from Driftkings.i18n import catalog
        self.i18n.clear()
        self.i18n.update(catalog.section(self.NAME, self.lang))

    def onPanelOpened(self):
        self.manager.reload(self)

    def onPanelClosed(self):
        pass

    def onButtonPress(self, name, value):
        pass
