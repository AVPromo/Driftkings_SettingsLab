# -*- coding: utf-8 -*-
from Driftkings._constants import BATTLE_EFFICIENCY
from Driftkings.settings.service import settings_service, affects
"""Presentation adapter for BattleEfficiency; gameplay state stays in its component."""


from Driftkings.core.overlay import overlays
from Driftkings.views.battle.label import CachedBattleLabel
from importlib import import_module


def _component():
    # Resolve live state after component initialization; avoid circular imports.
    return import_module('Driftkings.components.battle_efficiency')


class Flash(CachedBattleLabel):
    def __init__(self, ID):
        super(Flash, self).__init__(ID, _component, BATTLE_EFFICIENCY.POSITION, BATTLE_EFFICIENCY)
        self.setVisible(False)

    def onSettingsChanged(self, component, changes):
        if self._destroyed:
            return
        if affects(changes, BATTLE_EFFICIENCY.TEXT_LOCK, BATTLE_EFFICIENCY.POSITION):
            self.onApplySettings()
        if affects(changes, BATTLE_EFFICIENCY.TEXT_SHADOW):
            shadow = settings_service.getComponentDict(_component().config)[BATTLE_EFFICIENCY.TEXT_SHADOW]
            overlays.update(self.ID, {'shadow': shadow})

    def setVisible(self, visible):
        visible = bool(visible)
        if not self._destroyed and visible != self._lastVisible:
            if overlays.update(self.ID, {'visible': visible}):
                self._lastVisible = visible

    def addText(self, text):
        if self._destroyed:
            return
        text_style = settings_service.getComponentDict(_component().config)[BATTLE_EFFICIENCY.TEXT_STYLE]
        formatted_text = '<font size=\'%s\' face=\'%s\' color=\'%s\'><p align=\'%s\'>%s</p></font>' % (
            text_style['size'], text_style['font'], text_style['color'], text_style['align'], text)
        if formatted_text != self._lastText:
            if overlays.update(self.ID, {'text': formatted_text}):
                self._lastText = formatted_text


def _startFlash():
    _component().g_flash = Flash(_component().config.ID)
