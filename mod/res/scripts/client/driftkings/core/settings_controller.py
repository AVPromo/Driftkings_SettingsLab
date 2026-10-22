# -*- coding: utf-8 -*-
"""Idempotent settings subscriptions shared by long-lived controllers."""


class SettingsController(object):
    SETTINGS_SECTION = None

    def __init__(self):
        self.active = False

    def start(self):
        if self.active:
            return
        from driftkings.settings.service import settings_service
        self.active = True
        settings_service.onModSettingsChanged.connect(self.onSettingsChanged, self.SETTINGS_SECTION)

    def stop(self):
        if self.active:
            from driftkings.settings.service import settings_service
            self.active = False
            settings_service.onModSettingsChanged.disconnect(self.onSettingsChanged)
