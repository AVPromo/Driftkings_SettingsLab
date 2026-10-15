# -*- coding: utf-8 -*-
from Driftkings._constants import GLOBAL, MAIN_GUN
"""Presentation adapter for MainGun; gameplay state stays in its component."""
from Driftkings.settings.service import settings_service, affects
import os
import ResMgr
from Driftkings.common import logError
from Driftkings.core.overlay import overlays, ElementType, Align
from importlib import import_module


def _component():
    # Resolve live state after component initialization; avoid circular imports.
    return import_module('Driftkings.battle.main_gun')


class FlashController(object):
    def __init__(self, section):
        self.section = section
        self._visible = False
        self._destroyed = False
        self.setup()
        overlays.updated += self.__updatePosition
        settings_service.onModSettingsChanged.connect(self.onSettingsChanged, MAIN_GUN)

    def __updatePosition(self, alias, data):
        if alias != self.section:
            return
        settings_service.apply(_component().config, {MAIN_GUN.TEXT_POSITION: data})

    def onSettingsChanged(self, component, changes):
        if self._destroyed:
            return
        if affects(changes, MAIN_GUN.TEXT_POSITION, MAIN_GUN.TEXT_LOCK):
            settings = settings_service.getComponentDict(_component().config)
            overlays.update(self.section, dict(settings[MAIN_GUN.TEXT_POSITION],
                                         drag=not settings[MAIN_GUN.TEXT_LOCK], border=False))
        if affects(changes, MAIN_GUN.BACK_GROUND_ENABLED, (MAIN_GUN.BACKGROUND, 'alpha')):
            self.updateBackground()

    def updateBackground(self):
        settings = settings_service.getComponentDict(_component().config)
        opacity = max(0.0, min(1.0, float(settings[MAIN_GUN.BACKGROUND]['alpha']) / 100.0))
        overlays.update(self.section + '.image', {'alpha': opacity if self._visible and settings[MAIN_GUN.BACK_GROUND_ENABLED] else 0.0})

    def setup(self):
        bgPath = settings_service.getComponentDict(_component().config)[MAIN_GUN.BACKGROUND]['image']
        if bgPath in ('gui/maps/bg.png', '../maps/bg.png'):
            bgPath = '../maps/Driftkings/MainGun/bg.png'
        bgNormPath = os.path.normpath('gui/flash/' + bgPath).replace(os.sep, '/')
        bgSect = ResMgr.openSection(bgNormPath)
        if bgSect is None:
            logError(_component().config.NAME, 'Battle text background file not found: ' + bgNormPath)
        overlays.create(self.section, ElementType.PANEL, dict(settings_service.getComponentDict(_component().config)[MAIN_GUN.TEXT_POSITION], drag=not settings_service.getComponentDict(_component().config)[MAIN_GUN.TEXT_LOCK], border=False, limit=True, visible=False))
        self.createBox()

    def createBox(self):
        bgConf = settings_service.getComponentDict(_component().config)[MAIN_GUN.BACKGROUND]
        bgAltPath = '../maps/Driftkings/MainGun/bg.png'
        bgPath = bgConf['image']
        if bgPath in ('gui/maps/bg.png', '../maps/bg.png'):
            bgPath = bgAltPath
        width, height = bgConf['width'], bgConf['height']
        y = height
        overlays.create(self.section + '.text', ElementType.LABEL, {'text': '', 'width': width, 'height': height, 'alpha': 0.0, 'x': 0, 'y': y, 'alignX': Align.CENTER, 'alignY': Align.TOP})
        shadow = settings_service.getComponentDict(_component().config)[MAIN_GUN.SHADOW]
        if shadow['enabled']:
            overlays.update(self.section + '.text', {'shadow': shadow})
        overlays.create(self.section + '.image', ElementType.IMAGE, {'index': -1, 'image': bgPath, 'imageAlt': bgAltPath, 'width': width, 'height': height, 'alpha': 0.0, 'x': 0, 'y': y + 2, 'alignX': Align.CENTER, 'alignY': Align.TOP})

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True
        self._visible = False
        settings_service.onModSettingsChanged.disconnect(self.onSettingsChanged)
        overlays.updated -= self.__updatePosition
        overlays.remove(self.section + '.text')
        overlays.remove(self.section + '.image')
        overlays.remove(self.section)

    def hide(self):
        self._visible = False
        overlays.update(self.section, {'visible': False})
        overlays.update(self.section + '.text', {'alpha': 0.0})
        overlays.update(self.section + '.image', {'alpha': 0.0})

    def addText(self, text):
        if not settings_service.getComponentDict(_component().config)[GLOBAL.ENABLED]:
            return
        format_text = text if isinstance(text,type(u'')) else text.decode('utf-8') if isinstance(text,str) else type(u'')(text)
        self._visible = True
        overlays.update(self.section, {'visible': True})
        overlays.update(self.section + '.text', {'text': format_text})
        overlays.update(self.section + '.text', {'alpha': 1.0})
        self.updateBackground()


def _startFlash():
    _component().g_flash = FlashController(_component().config.NAME)
