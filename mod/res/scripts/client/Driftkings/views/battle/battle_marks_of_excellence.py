# -*- coding: utf-8 -*-
"""Owned Gameface child of WG 2.4.1 RandomHUDView; no Scaleform overlay."""
import logging
import weakref
from importlib import import_module

from Driftkings._constants import GLOBAL, BATTLE_MARKS_OF_EXCELLENCE
from Driftkings.core.marks_state import marks_state
from Driftkings.core.hud_visibility import hudVisibility
from Driftkings.settings.service import settings_service
from Driftkings.views.hangar.common import publish_card
from Driftkings.views.marks_model import finite

LOG = logging.getLogger('Driftkings.MarksOnGunBattle')
FEATURE = 'DriftkingsMarksOnGunBattle'


def _component():
    return import_module('Driftkings.battle.battle_marks_of_excellence')


class BattleMarksAdapter(object):
    def __init__(self):
        self.active = False
        self.visible = True
        self.hudVisible = True
        self.views = weakref.WeakKeyDictionary()
        self.installed = False

    def install(self):
        if self.installed:
            return
        from gui.impl.battle.random.hud import RandomHUDView
        from frameworks.wulf import ViewModel
        from gui.impl.pub.view_component import ViewComponent
        from gui.shared import events, EVENT_BUS_SCOPE
        from Driftkings.core.hooks import override
        from Driftkings.ui.gameface import attach_assets, resource_id
        from Driftkings.interface_catalog import gameface_spec
        adapter = self

        class MarksModel(ViewModel):
            def __init__(self):
                super(MarksModel, self).__init__(properties=3, commands=1)

            def _initialize(self):
                super(MarksModel, self)._initialize()
                self._addStringProperty('payload', '{}')
                self.onSavePosition = self._addCommand('onSavePosition')
                attach_assets(self, FEATURE)

        class MarksView(ViewComponent):
            def __init__(self, resource):
                self._lastPayload = None
                self._guiVisible = True
                self._cursorVisible = False
                self._ready = False
                self._attached = False
                self._lastVisible = None
                super(MarksView, self).__init__(layoutID=resource, model=MarksModel)

            def _onLoading(self, *args, **kwargs):
                super(MarksView, self)._onLoading(*args, **kwargs)

            def _onLoaded(self, *args, **kwargs):
                super(MarksView, self)._onLoaded(*args, **kwargs)
                import GUI
                self._cursorVisible = bool(GUI.mcursor().visible)
                self._ready = True
                LOG.info('Gameface battle panel loaded')
                adapter.refresh()

            def _getEvents(self):
                return tuple(super(MarksView, self)._getEvents()) + (
                    (self.getViewModel().onSavePosition, self._savePosition))

            def _savePosition(self, args):
                settings = settings_service.getComponentDict(_component().config)
                if not adapter.active or settings.get('gameface', {}).get('locked', True) or not isinstance(args, dict):
                    return
                x, y = finite(args.get('x')), finite(args.get('y'))
                if x is None or y is None:
                    return
                panel = dict(settings[BATTLE_MARKS_OF_EXCELLENCE.PANEL])
                panel.update(x=max(-7680, min(7680, x)), y=max(-4320, min(4320, y)))
                settings_service.apply(_component().config, {BATTLE_MARKS_OF_EXCELLENCE.PANEL: panel})

            def _getListeners(self):
                return tuple(super(MarksView, self)._getListeners()) + (
                    (events.GameEvent.GUI_VISIBILITY, self._visibility, EVENT_BUS_SCOPE.BATTLE),
                    (events.GameEvent.SHOW_CURSOR, self._showCursor, EVENT_BUS_SCOPE.GLOBAL),
                    (events.GameEvent.HIDE_CURSOR, self._hideCursor, EVENT_BUS_SCOPE.GLOBAL))

            def _showCursor(self, event):
                self._cursorVisible = True
                adapter.refresh()

            def _hideCursor(self, event):
                self._cursorVisible = False
                adapter.refresh()

            def _visibility(self, event):
                self._guiVisible = bool(event.ctx['visible'])
                adapter.refresh()

            def _finalize(self):
                self._ready = False
                for parent, child in list(adapter.views.items()):
                    if child is self:
                        adapter.views.pop(parent, None)
                super(MarksView, self)._finalize()

        @override(RandomHUDView, '_getChildComponents')
        def children(original, parent, *args, **kwargs):
            native = original(parent, *args, **kwargs)
            result = dict.fromkeys(native) if isinstance(native, tuple) else dict(native)
            try:
                resource = resource_id(gameface_spec(FEATURE)['resource'])
                if resource == -1:
                    LOG.warning('MarksOnGun battle resource is unavailable')
                    return result
                if resource in result:
                    LOG.warning('MarksOnGun battle resource already has an owner')
                    return result
                def create():
                    child = MarksView(resource)
                    adapter.views[parent] = child
                    LOG.info('Gameface battle panel created')
                    return child
                result[resource] = create
            except Exception:
                LOG.exception('Could not attach MarksOnGun Gameface battle panel')
            return result

        marks_state.changed.connect(self.onStateChanged)
        settings_service.onModSettingsChanged.connect(self.onSettingsChanged, BATTLE_MARKS_OF_EXCELLENCE)
        self.installed = True

    def startBattle(self):
        if self.active:
            return
        import BattleReplay
        settings = settings_service.getComponentDict(_component().config)
        if not settings[GLOBAL.ENABLED] or (BattleReplay.isPlaying() and not settings[BATTLE_MARKS_OF_EXCELLENCE.SHOW_IN_REPLAY]):
            return
        marks_state.clear('battle')
        self.active = True
        self.visible = True
        hudVisibility.attach(self)
        self.refresh()

    def stopBattle(self):
        self.active = False
        hudVisibility.detach(self)
        marks_state.clear('battle')
        self.refresh()

    def dispose(self):
        self.stopBattle()
        marks_state.changed.disconnect(self.onStateChanged)
        settings_service.onModSettingsChanged.disconnect(self.onSettingsChanged)
        from Driftkings.ui.gameface import resource_id
        from Driftkings.interface_catalog import gameface_spec
        resource = resource_id(gameface_spec(FEATURE)['resource'])
        for parent, child in list(self.views.items()):
            if parent.getChildView(resource) is child:
                child.setEnabled(False)
                child.destroy()
        self.views.clear()
        self.installed = False

    def onStateChanged(self, context):
        if context == 'battle':
            self.refresh()

    def onSettingsChanged(self, *args):
        self.refresh()

    def setBattleHudVisible(self, visible):
        self.hudVisible = visible
        self.refresh()

    def setupSize(self, *args):
        self.refresh()

    def setVisible(self, visible):
        if self.visible != visible:
            self.visible = visible
            self.refresh()

    def set_marks(self, payload):
        if not marks_state.publish('battle', payload):
            # Visibility can change without a numeric update.
            self.refresh()

    def unavailable(self, vehicle_id):
        self.visible = True
        marks_state.publish('battle', {'state': 'unavailable', 'vehicleId': vehicle_id})
        self.refresh()

    def refresh(self):
        settings = settings_service.getComponentDict(_component().config)
        config = dict(settings.get('gameface', {}))
        config.update(settings[BATTLE_MARKS_OF_EXCELLENCE.PANEL])
        config.update(scale=settings[BATTLE_MARKS_OF_EXCELLENCE.BATTLE_MESSAGE_SIZE_IN_PERCENT] / 100.0,
                      showStars=settings.get('showMarks', True), showTrend=settings.get('showDelta', True),
                      showCombined=settings.get('showDamage', True), showProgress=settings.get('showProgress', True))
        if not settings[BATTLE_MARKS_OF_EXCELLENCE.BACKGROUND]:
            config['backgroundOpacity'] = 0
        config['showTargetDamage'] = bool(config.get('showTargetDamage', True) and settings.get('showTargets', True))
        config['showRequiredDamage'] = bool(config.get('showRequiredDamage', True) and settings.get('showTargets', True))
        enabled = bool(self.active and self.visible and self.hudVisible and settings[GLOBAL.ENABLED]
                       and config.get('enabled', True) and config.get('visible', True))
        payload = marks_state.snapshot('battle')
        payload.update(config=config,
                       labels=dict((key[7:], value) for key, value in _component().config.i18n.items() if key.startswith('UI_mog_')))
        payload['labels']['title'] = _component().config.i18n['UI_description']
        from Driftkings.ui.gameface import resource_id
        from Driftkings.interface_catalog import gameface_spec
        resource = resource_id(gameface_spec(FEATURE)['resource'])
        for parent, child in list(self.views.items()):
            # Native child preparation can run before setChildView has returned.
            # Do not mistake a not-yet-attached child for an external replacement.
            if not child._ready:
                continue
            current = parent.getChildView(resource)
            if current is None and not child._attached:
                continue
            if current is not child:
                self.views.pop(parent, None)
                continue
            child._attached = True
            outgoing = dict(payload)
            outgoing['config'] = dict(config, visible=bool(enabled and child._guiVisible),
                                      draggable=bool(enabled and child._guiVisible and child._cursorVisible
                                                     and not config.get('locked', True)))
            try:
                publish_card(child, outgoing)
                visible = outgoing['config']['visible']
                if visible != child._lastVisible:
                    LOG.info('Gameface battle panel visible=%s state=%s', visible, outgoing.get('state'))
                    child._lastVisible = visible
            except Exception:
                LOG.exception('Could not publish MarksOnGun battle data')
