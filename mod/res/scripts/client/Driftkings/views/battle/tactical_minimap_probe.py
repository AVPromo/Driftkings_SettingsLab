# -*- coding: utf-8 -*-
"""Opt-in diagnostic child of RandomHUDView; never replaces native minimap UI."""
import logging
import weakref

from Driftkings.core.tactical_minimap_probe import accepts_ack, geometry_response, graphics_result, payload
from Driftkings.views.battle.tactical_minimap import native_adapter
from Driftkings.views.hangar.common import publish_card

LOG = logging.getLogger('Driftkings.TacticalMinimapProbe')
FEATURE = 'DriftkingsTacticalMinimapProbe'


class ProbeBridge(object):
    def __init__(self, config, settings_reader, adapter_factory=native_adapter, publisher=publish_card, schedule=None, cancel=None):
        self.config = config
        self._settings = settings_reader
        self._factory = adapter_factory
        self._publish = publisher
        self._schedule, self._cancel = schedule, cancel
        self._geometry_callback = None
        self.views = weakref.WeakSet()
        self.active = False
        self.generation = 0
        self._native_failed = False
        self.hudVisible = True
        self.disposed = False
        self.installed = False
        self._native = None
        self._adapter = None
        self._calibration = None
        self._ally_log_state = None
        self._ally_log_count = 0

    def enabled(self):
        if self.disposed:
            return False
        try:
            data = self._settings(self.config)
            return data.get('enabled', True) is True and data.get('tacticalDiagnostics', False) is True
        except Exception:
            return False

    def _close_adapter(self):
        if self._adapter is not None:
            self._adapter.close()
            self._adapter = None

    def bind_native(self, component):
        self._close_adapter()
        self._native_failed = False
        self._native = weakref.ref(component)
        self._read_geometry()
        self.refresh()

    def unbind_native(self, component):
        if self._native is not None and self._native() is component:
            self._close_adapter()
            self._native = None
            self._calibration = None
            self.refresh()

    def start(self, *args):
        if not self.enabled() or self.active:
            return
        from Driftkings.core.hud_visibility import hudVisibility
        self.generation += 1
        self._ally_log_state = None
        self._ally_log_count = 0
        for view in self.views:
            view._acknowledged = False
            view._graphicsResult = None
        self.active = True
        self._start_geometry_poll()
        hudVisibility.attach(self)
        self.refresh()

    def stop(self, *args):
        from Driftkings.core.hud_visibility import hudVisibility
        self.active = False
        if self._geometry_callback is not None:
            self._cancel(self._geometry_callback)
            self._geometry_callback = None
        self._native_failed = False
        for view in self.views:
            view._acknowledged = False
            view._graphicsResult = None
        hudVisibility.detach(self)
        self._close_adapter()
        self._native = None
        self._calibration = None
        self.refresh()

    def _read_geometry(self):
        component = self._native() if self._native is not None else None
        self._calibration = None
        if component is None or not self.enabled():
            return
        try:
            data = component.flashObject.as_DriftkingsMinimapGeometry()
            self._calibration = geometry_response(data)
        except Exception:
            self._calibration = {'available': False, 'reason': 'native-geometry-unavailable'}

    def _start_geometry_poll(self):
        if self._schedule is None:
            from Driftkings.core.callbacks import callback, cancelCallback
            self._schedule, self._cancel = callback, cancelCallback
        self._geometry_tick()

    def _geometry_tick(self):
        self._geometry_callback = None
        if not self.active or not self.enabled():
            self._calibration = None
            self.refresh()
            return
        if self.hudVisible and any(view._ready and view._guiVisible for view in self.views):
            self._read_geometry()
            self.refresh()
        self._geometry_callback = self._schedule(0.25, self._geometry_tick)

    def setBattleHudVisible(self, visible):
        self.hudVisible = bool(visible)
        self.refresh()

    def acknowledge(self, view, args):
        if (self.active and self.enabled() and view in self.views and
                view._ready and accepts_ack(args, self.generation) and not view._acknowledged):
            view._acknowledged = True
            view._graphicsResult = graphics_result(args)
            if view._graphicsResult is not None:
                LOG.info('Graphics diagnostic: SVG DOM=%s glyph nodes=%d/21; visual confirmation required',
                         view._graphicsResult['svgApi'], view._graphicsResult['glyphCount'])
            LOG.info('Gameface diagnostic handshake confirmed (protocol 1); Vanilla unchanged')
            self.refresh()

    def refresh(self, *args):
        enabled = self.active and self.enabled() and self.hudVisible
        ready_views = [view for view in self.views if view._ready]
        snapshot = None
        if enabled and any(view._guiVisible for view in ready_views):
            component = self._native() if self._native is not None else None
            if component is not None and self._native_failed:
                snapshot = {'source': 'native-minimap-audit', 'reason': 'native-adapter-unavailable'}
            elif component is not None:
                try:
                    if self._adapter is None:
                        self._adapter = self._factory(component, component.sessionProvider)
                    snapshot = self._adapter.capture()
                except Exception:
                    self._close_adapter()
                    self._native_failed = True
                    snapshot = {'source': 'native-minimap-audit', 'reason': 'native-adapter-unavailable'}
                    LOG.exception('Native diagnostic adapter unavailable; Vanilla unchanged')
        for view in ready_views:
            try:
                data = payload(enabled and view._guiVisible, view._acknowledged, snapshot, self.generation,
                               getattr(view, '_graphicsResult', None), self._calibration)
                state = (data['allyStatus'], data['reason'], 'ready' if (self._calibration or {}).get('available') else (self._calibration or {}).get('reason', 'no-native-geometry'))
                if enabled and state != self._ally_log_state and self._ally_log_count < 8:
                    self._ally_log_state = state
                    self._ally_log_count += 1
                    LOG.info('Allied calibration: status=%s native=%s geometry=%s entries=%d audit=%s',
                             state[0], state[1], state[2], data['markerCount'], (snapshot or {}).get('entryAudit', {}))
                self._publish(view, data)
            except Exception:
                LOG.exception('Cannot publish minimap diagnostic; Vanilla unchanged')

    def dispose(self):
        if self.disposed:
            return
        self.disposed = True
        self.stop()
        for view in list(self.views):
            try:
                view.destroy()
            except Exception:
                LOG.exception('Cannot destroy diagnostic view')
        self.views.clear()

    def install(self):
        if self.installed or not self.enabled():
            return
        from frameworks.wulf import ViewModel
        from gui.impl.pub.view_component import ViewComponent
        from gui.impl.battle.random.hud import RandomHUDView
        from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent
        from gui.shared import events, EVENT_BUS_SCOPE
        from Driftkings.core.hooks import override, on_event
        from Driftkings.core.battle_events import battleEvents
        from Driftkings.ui.gameface import attach_assets, resource_id
        from Driftkings.interface_catalog import gameface_spec
        bridge = self

        class ProbeModel(ViewModel):
            def __init__(self):
                super(ProbeModel, self).__init__(properties=3, commands=1)

            def _initialize(self):
                super(ProbeModel, self)._initialize()
                self._addStringProperty('payload', '{}')
                self.onProbeReady = self._addCommand('onProbeReady')
                attach_assets(self, FEATURE)

        class ProbeView(ViewComponent):
            def __init__(self, layout_id):
                self._ready = False
                self._guiVisible = True
                self._acknowledged = False
                self._graphicsResult = None
                self._lastPayload = None
                super(ProbeView, self).__init__(layoutID=layout_id, model=ProbeModel)
                bridge.views.add(self)

            def _onLoaded(self, *args, **kwargs):
                super(ProbeView, self)._onLoaded(*args, **kwargs)
                self._ready = True
                LOG.info('Gameface diagnostic view loaded; awaiting handshake')
                bridge.refresh()

            def _getEvents(self):
                return tuple(super(ProbeView, self)._getEvents()) + (
                    (self.getViewModel().onProbeReady, self._ack),)

            def _ack(self, args):
                bridge.acknowledge(self, args)

            def _getListeners(self):
                return tuple(super(ProbeView, self)._getListeners()) + (
                    (events.GameEvent.GUI_VISIBILITY, self._visibility, EVENT_BUS_SCOPE.BATTLE),)

            def _visibility(self, event):
                self._guiVisible = bool(event.ctx['visible'])
                bridge.refresh()

            def _finalize(self):
                self._ready = False
                bridge.views.discard(self)
                super(ProbeView, self)._finalize()

        @override(RandomHUDView, '_getChildComponents')
        def children(original, parent, *args, **kwargs):
            native = original(parent, *args, **kwargs)
            if not bridge.enabled():
                return native
            try:
                resource = resource_id(gameface_spec(FEATURE)['resource'])
                if resource == -1 or resource in native:
                    LOG.warning('Minimap diagnostic resource unavailable or already owned')
                    return native
                result = dict.fromkeys(native) if isinstance(native, tuple) else dict(native)
                def create():
                    try:
                        return ProbeView(resource)
                    except Exception:
                        # ViewComponent._constructChild skips None without aborting native children.
                        LOG.exception('Cannot construct minimap diagnostic; native HUD unchanged')
                        return None
                result[resource] = create
                return result
            except Exception:
                LOG.exception('Cannot attach diagnostic child; native HUD unchanged')
                return native

        @override(MinimapComponent, '_populate')
        def populate(original, component, *args, **kwargs):
            result = original(component, *args, **kwargs)
            try:
                if bridge.enabled():
                    bridge.bind_native(component)
            except Exception:
                LOG.exception('Cannot bind native diagnostic source')
            return result

        @override(MinimapComponent, '_dispose')
        def dispose_native(original, component, *args, **kwargs):
            try:
                bridge.unbind_native(component)
            except Exception:
                LOG.exception('Cannot release native diagnostic source')
            return original(component, *args, **kwargs)

        on_event(battleEvents.started, self.start)
        on_event(battleEvents.loaded, self.refresh)
        on_event(battleEvents.visibility, self.refresh)
        on_event(battleEvents.ended, self.stop)
        self.installed = True
        LOG.info('Diagnostic bridge enabled for next RandomHUD battle; native minimap remains in control')
