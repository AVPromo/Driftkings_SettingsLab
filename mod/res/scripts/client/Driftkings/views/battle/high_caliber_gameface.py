# -*- coding: utf-8 -*-
"""MainGun HUD presentation. All targets and states arrive from the battle component."""
import logging
import weakref
from importlib import import_module

from Driftkings._constants import GLOBAL, HIGH_CALIBER_PROGRESS
from Driftkings.core.hud_visibility import hudVisibility
from Driftkings.settings.service import settings_service
from Driftkings.views.hangar.common import publish_card
from Driftkings.views.marks_model import finite, number_locale

LOG = logging.getLogger('Driftkings.MainGunBattle')
FEATURE = 'DriftkingsMainGun'


def _component():
    return import_module('Driftkings.battle.high_caliber_progress')


class MainGunAdapter(object):
    def __init__(self):
        self.active = True
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

        class HighCaliberModel(ViewModel):
            def __init__(self):
                super(HighCaliberModel, self).__init__(properties=3, commands=1)

            def _initialize(self):
                super(HighCaliberModel, self)._initialize()
                self._addStringProperty('payload', '{}')
                self.onSavePosition = self._addCommand('onSavePosition')
                attach_assets(self, FEATURE)

        class HighCaliberView(ViewComponent):
            def __init__(self, resource):
                self._lastPayload = None
                self._guiVisible = True
                self._cursorVisible = False
                self._ready = False
                self._attached = False
                self._lastVisible = None
                super(HighCaliberView, self).__init__(layoutID=resource, model=HighCaliberModel)

            def _onLoaded(self, *args, **kwargs):
                super(HighCaliberView, self)._onLoaded(*args, **kwargs)
                import GUI
                self._cursorVisible = bool(GUI.mcursor().visible)
                self._ready = True
                LOG.info('Gameface battle panel loaded')
                adapter.refresh()

            def _getEvents(self):
                return tuple(super(HighCaliberView, self)._getEvents()) + (
                    (self.getViewModel().onSavePosition, self._savePosition),)

            def _savePosition(self, args):
                settings = settings_service.getComponentDict(_component().config)
                if (not adapter.active or not adapter.hudVisible or not self._guiVisible
                        or not self._cursorVisible or settings.get('textLock', False)
                        or not _component().mainGuns.payload.get('visible')
                        or not isinstance(args, dict)):
                    return
                x, y = finite(args.get('x')), finite(args.get('y'))
                if x is None or y is None:
                    return
                panel = dict(settings[HIGH_CALIBER_PROGRESS.TEXT_POSITION])
                panel.update(x=max(-7680, min(7680, x)), y=max(-4320, min(4320, y)))
                settings_service.apply(_component().config, {HIGH_CALIBER_PROGRESS.TEXT_POSITION: panel})

            def _getListeners(self):
                return tuple(super(HighCaliberView, self)._getListeners()) + (
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
                super(HighCaliberView, self)._finalize()

        @override(RandomHUDView, '_getChildComponents')
        def children(original, parent, *args, **kwargs):
            native = original(parent, *args, **kwargs)
            result = dict.fromkeys(native) if isinstance(native, tuple) else dict(native)
            try:
                resource = resource_id(gameface_spec(FEATURE)['resource'])
                if resource == -1:
                    LOG.warning('MainGun battle resource is unavailable')
                    return result
                if resource in result:
                    LOG.warning('MainGun battle resource already has an owner')
                    return result
                def create():
                    child = HighCaliberView(resource)
                    adapter.views[parent] = child
                    LOG.info('Gameface battle panel created')
                    return child
                result[resource] = create
            except Exception:
                LOG.exception('Could not attach MainGun Gameface battle panel')
            return result

        settings_service.onModSettingsChanged.connect(self.onSettingsChanged, HIGH_CALIBER_PROGRESS)
        self.installed = True
        hudVisibility.attach(self)

    def dispose(self):
        self.active = False
        hudVisibility.detach(self)
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

    def refresh(self):
        settings = settings_service.getComponentDict(_component().config)
        config = dict(settings.get('gameface', {}))
        config.update(settings[HIGH_CALIBER_PROGRESS.TEXT_POSITION])
        config.update(locked=settings['textLock'],
                      backgroundColor='#0f1216',
                      backgroundOpacity=max(0, min(1, settings['background']['alpha'] / 100.0))
                      if settings['backGroundEnabled'] else 0)
        payload = dict(_component().mainGuns.payload)
        enabled = bool(self.active and self.visible and self.hudVisible and settings[GLOBAL.ENABLED]
                       and payload.get('visible'))
        labels = _component().config.i18n
        unavailable = payload.get('state') == 'unavailable'
        value = payload.get('damage', 0) if payload.get('state') == 'achieved' else payload.get('remaining', 0)
        group = number_locale(_component().config.lang)['groupSeparator']
        payload.update(config=config,
                       primaryText=labels['UI_hc_unavailable'] if unavailable else
                       u'{:,}'.format(int(value)).replace(',', group) + ' HP',
                       secondaryText=labels['UI_hc_' + (payload.get('reason') or payload.get('state', 'progress'))],
                       progressText=u'%d%%' % payload.get('progress', 0),
                       progressLabel=labels['UI_hc_progressLabel'])
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
                LOG.exception('Could not publish MainGun battle data')
