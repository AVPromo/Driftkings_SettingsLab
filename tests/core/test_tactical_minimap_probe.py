# -*- coding: utf-8 -*-
import json
import io
import os

from support import ROOT, RuntimeTest, module, source


class Owner(object):
    def __init__(self, **values):
        self.__dict__.update(values)


class ProbeTests(RuntimeTest):
    def setUp(self):
        super(ProbeTests, self).setUp()
        self.policy = self.load('core.tactical_minimap_probe')
        self.settings = {'enabled': True, 'tacticalDiagnostics': False}
        self.frames, self.factory_calls, self.closed = [], [], []
        self.snapshot = {'source': 'native-minimap-audit', 'available': True,
                         'bounds': [-1, -1, 1, 1], 'nativeSize': [210, 210], 'texture': 'test.dds',
                         'markers': [{'id': 666, 'x': .25, 'y': .5, 'name': 'secret-marker'}]}
        self.fail_factory = False
        self.attached = []
        hud = Owner(attach=lambda view: self.attached.append(view),
                    detach=lambda view: self.attached.remove(view) if view in self.attached else None)
        def factory(component, session):
            self.factory_calls.append(component)
            if self.fail_factory:
                raise ValueError('Simulated unavailable Gameface/native contract')
            return Owner(capture=lambda: self.snapshot, close=lambda: self.closed.append(True))
        def publish(view, data):
            self.frames.append(data)
        self.scheduled, self.cancelled = [], []
        self.api = source('views/battle/tactical_minimap_probe.py', {
            'Driftkings.core.tactical_minimap_probe': self.policy,
            'Driftkings.views.battle.tactical_minimap': module(native_adapter=factory, native_player_point=lambda component, record: None, native_objective_points=lambda component, records: []),
            'Driftkings.views.hangar.common': module(publish_card=publish),
            'Driftkings.core.hud_visibility': module(hudVisibility=hud)})
        self.bridge = self.api['ProbeBridge'](object(), lambda config: self.settings,
            schedule=lambda delay, fn: self.scheduled.append((delay, fn)) or len(self.scheduled),
            cancel=lambda token: self.cancelled.append(token))
        self.view = Owner(_ready=True, _guiVisible=True, _acknowledged=False, destroy=lambda: None)
        self.bridge.views.add(self.view)
        self.component = Owner(sessionProvider=Owner(),
            flashObject=Owner(as_DriftkingsMinimapGeometry=lambda *args: '1|800|400|200|200|1000|800'))

    def test_map_uri_accepts_only_virtual_cartography(self):
        for path in ('spaces/01_karelia/mmap.dds', 'gui/maps/icons/map/01_karelia.png'):
            self.assertEqual(self.policy.texture_uri(path), 'img://' + path)
        for path in ('https://example.com/map.png', 'spaces/../secret.dds',
                     'spaces//map.dds', 'mods/configs/map.png', 'spaces/map.dds\n'):
            self.assertIsNone(self.policy.texture_uri(path))

    def test_calibration_is_bounded_and_contains_only_geometry(self):
        raw = dict(available=True, x=800, y=400, width=200, height=200,
                   stageWidth=1000, stageHeight=800, markers=['secret'])
        result = self.policy.calibration_result(raw)
        self.assertTrue(result['available'])
        self.assertEqual(result['normalized']['x'], .8)
        self.assertNotIn('markers', result)
        raw['width'] = float('nan')
        self.assertFalse(self.policy.calibration_result(raw)['available'])
        self.assertNotIn('calibration', self.policy.payload(False, False, calibration=raw))

    def test_native_geometry_does_not_require_an_auxiliary_view(self):
        self.settings['tacticalDiagnostics'] = True
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.assertTrue(self.bridge._calibration['available'])
        self.assertEqual(self.scheduled[0][0], .25)
        self.bridge.unbind_native(self.component)
        self.assertIsNone(self.bridge._calibration)
        self.bridge.stop()
        self.assertEqual(self.cancelled, [1])
        self.assertIsNone(self.bridge._geometry_callback)

    def test_geometry_string_protocol_is_bounded_and_rejects_invalid_data(self):
        self.assertTrue(self.policy.geometry_response('1|800|400|200|200|1000|800')['available'])
        for value in (None, {}, '1|0|0|nan|200|1000|800', '1|0|0|-1|200|1000|800', '1|0', '2|0'):
            self.assertFalse(self.policy.geometry_response(value)['available'])

    def test_ally_probe_requires_handshake_geometry_and_current_publication(self):
        geometry = dict(available=True, x=800, y=400, width=200, height=200,
                        stageWidth=1000, stageHeight=800)
        marker = dict(id=666, name='secret-marker', side='ally', visible=True,
                      state='visible', x=.25, y=.5)
        self.snapshot['markers'] = [marker]
        self.assertNotIn('alliedPoint', self.policy.payload(True, False, self.snapshot, calibration=geometry))
        self.assertNotIn('alliedPoint', self.policy.payload(True, True, self.snapshot))
        data = self.policy.payload(True, True, self.snapshot, calibration=geometry)
        self.assertEqual(data['alliedPoint'], {'x': .25, 'y': .5})
        self.assertEqual(data['allyStatus'], 'ready')
        self.assertEqual(self.policy.payload(True, False, self.snapshot)['allyStatus'], 'waiting-handshake')
        self.assertEqual(self.policy.payload(True, True, self.snapshot)['allyStatus'], 'waiting-geometry')
        self.assertNotIn('secret-marker', json.dumps(data))
        for changes in ({'side': 'enemy'}, {'visible': False}, {'state': 'lost'},
                        {'x': float('nan')}, {'y': 1.1}):
            invalid = dict(marker, **changes)
            self.assertIsNone(self.policy.allied_calibration_point([invalid]))
        self.snapshot['markers'] = []
        self.assertNotIn('alliedPoint', self.policy.payload(True, True, self.snapshot, calibration=geometry))

    def test_native_geometry_poll_handles_failure_recovery_hud_and_stop(self):
        self.settings['tacticalDiagnostics'] = True
        self.bridge.bind_native(self.component)
        self.bridge.start()
        def missing(*args):
            raise AttributeError('Library not ready')
        self.component.flashObject.as_DriftkingsMinimapGeometry = missing
        self.scheduled[-1][1]()
        self.assertEqual(self.bridge._calibration['reason'], 'native-geometry-unavailable')
        self.component.flashObject.as_DriftkingsMinimapGeometry = lambda *args: '1|0|0|200|200|1000|800'
        self.scheduled[-1][1]()
        self.assertTrue(self.bridge._calibration['available'])
        self.bridge.hudVisible = False
        self.component.flashObject.as_DriftkingsMinimapGeometry = missing
        self.scheduled[-1][1]()
        self.assertTrue(self.bridge._calibration['available'])
        self.bridge.stop()
        count = len(self.scheduled)
        self.bridge._geometry_tick()
        self.assertEqual(len(self.scheduled), count)
        self.assertIsNone(self.bridge._calibration)

    def test_native_cell_name_is_whitelisted_without_recomputing_boundaries(self):
        marker = dict(side='ally', visible=True, state='visible', x=.25, y=.5)
        for row in 'ABCDEFGHJK':
            for column in '1234567890':
                marker['cell'] = row + column
                self.assertEqual(self.policy.allied_calibration_point([marker])['cell'], row + column)
        for invalid in ('I5', 'A10', 'Z0', 'A1\n', '<b>A1</b>', None):
            marker['cell'] = invalid
            self.assertNotIn('cell', self.policy.allied_calibration_point([marker]))

    def test_allied_class_transport_is_limited_to_native_classes_and_relations(self):
        marker = dict(side='platoon', visible=True, state='visible', x=.25, y=.5,
                      name='private', id=666)
        for vehicle_class in ('lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG'):
            marker['vehicleClass'] = vehicle_class
            point = self.policy.allied_calibration_point([marker])
            self.assertEqual(point['vehicleClass'], vehicle_class)
            self.assertEqual(point['side'], 'platoon')
            self.assertNotIn('name', point)
            self.assertNotIn('id', point)
        marker['vehicleClass'] = 'unknown'
        self.assertNotIn('vehicleClass', self.policy.allied_calibration_point([marker]))
        marker['side'] = 'enemy'
        self.assertIsNone(self.policy.allied_calibration_point([marker]))

    def test_allied_frame_is_bounded_current_and_excludes_enemies_and_identity(self):
        ally = dict(side='ally', visible=True, state='visible', vehicleClass='mediumTank',
                    x=.25, y=.5, name='private', id=666)
        platoon = dict(ally, side='platoon', x=.75)
        self.assertEqual(len(self.policy.allied_calibration_points([ally, platoon])), 2)
        rejected = [dict(ally, side='enemy'), dict(ally, visible=False),
                    dict(ally, state='lost'), dict(ally, x=float('nan'))]
        self.assertEqual(self.policy.allied_calibration_points(rejected), [])
        rows = self.policy.allied_calibration_points([ally] * 100)
        self.assertEqual(len(rows), 64)
        self.assertNotIn('private', json.dumps(rows))
        self.assertNotIn('666', json.dumps(rows))
        self.assertEqual(self.policy.allied_calibration_points([]), [])
        self.assertEqual(self.policy.allied_calibration_points(None), [])

    def test_own_published_vehicle_keeps_player_relation_without_identity(self):
        marker = dict(side='player', visible=True, state='visible', vehicleClass='mediumTank',
                      x=.25, y=.5, id=666, name='private')
        point = self.policy.allied_calibration_points([marker])[0]
        self.assertEqual(point['side'], 'player')
        self.assertNotIn('id', point)
        self.assertNotIn('name', point)
        self.assertEqual(self.policy.allied_calibration_points([dict(marker, visible=False)]), [])

    def test_personal_player_protocol_is_validated_and_replaces_duplicate(self):
        geometry = self.policy.geometry_response('1|0|0|200|200|1000|800')
        geometry['player'] = self.policy.player_point({'x': .25, 'y': .75, 'heading': 90})
        self.assertEqual(geometry['player'], {'x': .25, 'y': .75, 'heading': 90, 'side': 'player'})
        self.snapshot['markers'] = [dict(side='player', visible=True, state='visible',
                                        vehicleClass='mediumTank', x=.2, y=.7)]
        data = self.policy.payload(True, True, self.snapshot, calibration=geometry)
        self.assertEqual(data['alliedPoints'], [geometry['player']])
        for value in ({'x': float('nan'), 'y': .5, 'heading': 90},
                      {'x': .5, 'y': .5, 'heading': 360}, {'x': 2, 'y': .5, 'heading': 90}):
            self.assertIsNone(self.policy.player_point(value))
        geometry = self.policy.geometry_response('1|0|0|200|200|1000|800')
        self.snapshot['markers'] = []
        self.assertEqual(self.policy.payload(True, True, self.snapshot, calibration=geometry)['alliedPoints'], [])

    def test_personal_publication_tracks_matrix_active_and_delete_without_history(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component, matrix = Owner(), object()
        calls = []
        def add(original_component, symbol, container, provider, active, *args, **kwargs):
            calls.append((symbol, container, provider, active))
            return 123
        self.assertEqual(hooks['addEntry'](add, component, 'ViewPointEntry', 'personal', matrix, True), 123)
        self.assertEqual(bridge._personal_entries[component], {'id': 123, 'matrix': matrix, 'active': True})
        replacement = object()
        self.assertEqual(hooks['setMatrix'](lambda *args: 'native', component, 123, replacement), 'native')
        self.assertIs(bridge._personal_entries[component]['matrix'], replacement)
        hooks['setActive'](lambda *args: None, component, 123, False)
        self.assertFalse(bridge._personal_entries[component]['active'])
        hooks['delEntry'](lambda *args: None, component, 123)
        self.assertNotIn(component, bridge._personal_entries)
        hooks['addEntry'](add, component, 'VehicleEntry', 'aliveVehicles', matrix, True)
        self.assertNotIn(component, bridge._personal_entries)

    def test_objective_contract_is_bounded_and_strips_identity(self):
        rows = [dict(kind=kind, x=.25, y=.5, id=666, text='private')
                for kind in ('allyBase', 'enemyBase', 'controlPoint')]
        clean = self.policy.objective_points(rows)
        self.assertEqual(len(clean), 3)
        self.assertNotIn('666', json.dumps(clean))
        self.assertNotIn('private', json.dumps(clean))
        self.assertEqual(self.policy.objective_points([dict(kind='enemyVehicle', x=.5, y=.5)]), [])
        self.assertEqual(self.policy.objective_points([dict(kind='allyBase', x=float('nan'), y=.5)]), [])
        self.assertEqual(len(self.policy.objective_points(rows * 20)), 16)

    def test_native_objective_publication_reuses_existing_hooks_and_removes_state(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component, matrix = Owner(), object()
        native = lambda *args: 42
        hooks['addEntry'](native, component, 'AllyTeamBaseEntry', 'points', matrix, True)
        self.assertEqual(bridge._objective_entries[component][42]['kind'], 'allyBase')
        self.assertEqual(hooks['invoke'](native, component, 42, 'setPointNumber', 2), 42)
        self.assertEqual(bridge._objective_entries[component][42]['number'], 2)
        hooks['invoke'](native, component, 42, 'setPointNumber', True)
        self.assertEqual(bridge._objective_entries[component][42]['number'], 2)
        hooks['setActive'](native, component, 42, False)
        self.assertFalse(bridge._objective_entries[component][42]['active'])
        other = object()
        hooks['setMatrix'](native, component, 42, other)
        self.assertIs(bridge._objective_entries[component][42]['matrix'], other)
        hooks['delEntry'](native, component, 42)
        self.assertEqual(bridge._objective_entries[component], {})
        hooks['addEntry'](native, component, 'EnemyVehicleEntry', 'points', matrix, True)
        self.assertEqual(bridge._objective_entries[component], {})
        hooks['addEntry'](native, component, 'EnemyTeamBaseEntry', 'points', matrix, True)
        bridge.stop()
        self.assertEqual(len(bridge._objective_entries), 0)

    def test_capture_metadata_is_whitelisted_and_bounded(self):
        value = dict(kind='allyBase', x=.2, y=.3, number=2, state='blocked', progress=42)
        clean = self.policy.objective_points([value])[0]
        self.assertEqual((clean['number'], clean['state'], clean['progress']), (2, 'blocked', 42))
        value.update(number=True, state='invented', progress=float('nan'))
        clean = self.policy.objective_points([value])[0]
        self.assertNotIn('number', clean)
        self.assertEqual(clean['state'], 'unknown')
        self.assertNotIn('progress', clean)

    def test_default_off_creates_no_adapter_and_starts_no_diagnostic(self):
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.assertFalse(self.bridge.active)
        self.assertEqual(self.factory_calls, [])
        self.assertEqual(self.attached, [])
        self.assertFalse(self.frames[-1]['enabled'])

    def test_summary_never_transports_vehicle_ids_names_or_coordinates(self):
        data = self.policy.payload(True, True, self.snapshot, 1)
        self.assertEqual(data['markerCount'], 1)
        self.assertNotIn('markers', data)
        encoded = json.dumps(data)
        self.assertNotIn('secret-marker', encoded)
        self.assertNotIn('666', encoded)
        self.assertEqual(data['effectiveMode'], 'vanilla')
        self.assertFalse(data['nativePresentationChanged'])
        self.assertFalse(data['lostContactAvailable'])

    def test_disabled_or_malformed_metadata_returns_no_map_information(self):
        self.assertNotIn('texture', self.policy.payload(False, True, self.snapshot))
        self.snapshot['bounds'][0] = float('nan')
        result = self.policy.payload(True, False, self.snapshot)
        self.assertFalse(result['available'])
        self.assertEqual(result['reason'], 'invalid-native-metadata')

    def test_handshake_is_once_per_generation_and_stale_commands_are_rejected(self):
        self.settings['tacticalDiagnostics'] = True
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.bridge.start()
        self.assertEqual(self.bridge.generation, 1)
        for args in ({'protocol': True, 'generation': 1}, {'protocol': 2, 'generation': 1},
                     {'protocol': 1, 'generation': 0}, None):
            self.bridge.acknowledge(self.view, args)
            self.assertFalse(self.view._acknowledged)
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.assertTrue(self.view._acknowledged)
        self.assertEqual(self.frames[-1]['reason'], 'ready')
        frame_count = len(self.frames)
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.assertEqual(len(self.frames), frame_count)
        self.bridge.stop()
        self.bridge.start()
        self.assertEqual(self.bridge.generation, 2)
        self.assertFalse(self.view._acknowledged)
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.assertFalse(self.view._acknowledged)
        self.bridge.acknowledge(self.view, {'protocol': 1.0, 'generation': 2.0})
        self.assertTrue(self.view._acknowledged)

    def test_native_failure_is_isolated_and_not_retried_on_every_event(self):
        self.settings['tacticalDiagnostics'] = True
        self.fail_factory = True
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.bridge.refresh()
        self.assertEqual(len(self.factory_calls), 1)
        self.assertFalse(self.frames[-1]['available'])
        self.assertEqual(self.frames[-1]['reason'], 'native-adapter-unavailable')
        self.assertFalse(self.frames[-1]['nativePresentationChanged'])

    def test_stale_native_disposal_does_not_remove_new_component(self):
        self.settings['tacticalDiagnostics'] = True
        self.bridge.start()
        old = self.component
        self.bridge.bind_native(old)
        self.component = Owner(sessionProvider=Owner())
        self.bridge.bind_native(self.component)
        self.bridge.unbind_native(old)
        self.assertIs(self.bridge._native(), self.component)
        self.bridge.unbind_native(self.component)
        self.assertIsNone(self.bridge._native)
        self.assertTrue(self.closed)

    def test_no_capture_when_hud_hidden_or_no_loaded_view_and_dispose_releases(self):
        self.settings['tacticalDiagnostics'] = True
        self.view._ready = False
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.assertEqual(self.factory_calls, [])
        self.view._ready = True
        self.bridge.setBattleHudVisible(False)
        self.assertEqual(self.factory_calls, [])
        self.bridge.setBattleHudVisible(True)
        self.assertEqual(len(self.factory_calls), 1)
        self.bridge.dispose()
        self.bridge.dispose()
        self.assertFalse(self.bridge.active)
        self.assertFalse(self.bridge.enabled())
        self.assertEqual(len(self.bridge.views), 0)
        self.assertEqual(self.attached, [])
        self.assertEqual(len(self.closed), 1)


    def install_runtime_stubs(self):
        hooks, events = {}, []
        fixture = self
        class BaseModel(object):
            def __init__(self, **kwargs):
                self.sizes = kwargs
            def _initialize(self):
                pass
            def _addStringProperty(self, *args):
                pass
            def _addCommand(self, name):
                return object()
        class BaseView(object):
            def __init__(self, layoutID, model):
                if fixture.fail_construction:
                    raise RuntimeError('Simulated failed Gameface construction')
                self.model = model()
                self.model._initialize()
            def _onLoaded(self, *args):
                pass
            def _finalize(self):
                pass
            def getViewModel(self):
                return self.model
            def _getEvents(self):
                return ()
            def _getListeners(self):
                return ()
            def destroy(self):
                self._finalize()
        class NativeHUD(object):
            pass
        class NativeMap(object):
            pass
        def override(target, name):
            def decorate(fn):
                hooks[name] = fn
                return fn
            return decorate
        self.fail_construction = False
        self.resource_id = 123
        dependencies = {
            'Driftkings.core.tactical_minimap_probe': self.policy,
            'Driftkings.views.battle.tactical_minimap': module(native_adapter=lambda *args: None, native_player_point=lambda component, record: None, native_objective_points=lambda component, records: []),
            'Driftkings.views.hangar.common': module(publish_card=lambda *args: None),
            'frameworks.wulf': module(ViewModel=BaseModel),
            'gui.impl.pub.view_component': module(ViewComponent=BaseView),
            'gui.impl.battle.random.hud': module(RandomHUDView=NativeHUD),
            'gui.Scaleform.daapi.view.battle.shared.minimap.component': module(MinimapComponent=NativeMap),
            'gui.shared': module(events=module(GameEvent=module(GUI_VISIBILITY=1)), EVENT_BUS_SCOPE=module(BATTLE=2)),
            'Driftkings.core.hooks': module(override=override, on_event=lambda signal, fn: events.append((signal, fn))),
            'Driftkings.core.battle_events': module(battleEvents=module(started=1, loaded=2, visibility=3, ended=4)),
            'Driftkings.ui.gameface': module(attach_assets=lambda *args: None, resource_id=lambda key: self.resource_id),
            'Driftkings.interface_catalog': module(gameface_spec=lambda key: {'resource': 'mods/Driftkings/TacticalMinimapProbe/model'})}
        bridge = source('views/battle/tactical_minimap_probe.py', dependencies)['ProbeBridge'](
            object(), lambda config: self.settings)
        return bridge, hooks, events

    def test_default_off_installs_no_hooks_or_event_subscriptions(self):
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        self.assertFalse(bridge.installed)
        self.assertEqual(hooks, {})
        self.assertEqual(events, [])

    def test_hud_hook_preserves_native_children_and_missing_resource(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        bridge.install()
        self.assertEqual(len(hooks), 8)
        self.assertEqual(len(events), 4)
        native = {7: object()}
        children = hooks['_getChildComponents'](lambda parent: native, Owner())
        self.assertIs(children[7], native[7])
        self.assertNotIn(123, native)
        self.assertIn(123, children)
        view = children[123]()
        self.assertIsNotNone(view)
        self.assertEqual(view.model.sizes, {'properties': 3, 'commands': 1})
        self.assertEqual(len(view._getEvents()), 1)
        self.resource_id = -1
        self.assertIs(hooks['_getChildComponents'](lambda parent: native, Owner()), native)

    def test_failed_probe_construction_is_skipped_without_raising_into_native_hud(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        self.fail_construction = True
        native = (7, 8)
        children = hooks['_getChildComponents'](lambda parent: native, Owner())
        self.assertEqual(children[7], None)
        self.assertEqual(children[8], None)
        self.assertIsNone(children[123]())


    def test_canonical_defaults_keep_probe_off_for_legacy_and_split_storage(self):
        for relative in ('res/configs/Driftkings/default/minimap_enhancements.json',
                         'res/configs/Driftkings/default/minimap_enhancements/minimap.json'):
            with io.open(os.path.join(ROOT, *relative.split('/')), encoding='utf-8') as stream:
                self.assertIs(json.load(stream)['tacticalDiagnostics'], False)


    def test_graphics_report_is_bounded_and_does_not_imply_production_support(self):
        result = self.policy.graphics_result({'svgApi': True, 'glyphCount': 21, 'positions': ['private']})
        self.assertEqual(result, {'svgApi': True, 'glyphCount': 21})
        self.assertEqual(self.policy.graphics_result({'svgApi': False, 'glyphCount': 0}),
                         {'svgApi': False, 'glyphCount': 0})
        for args in ({'svgApi': True, 'glyphCount': 20}, {'svgApi': 'yes', 'glyphCount': 21},
                     {'svgApi': False, 'glyphCount': True}, {'svgApi': True, 'glyphCount': 22},
                     {'svgApi': False, 'glyphCount': float('nan')}, {'svgApi': False, 'glyphCount': 2.5}):
            self.assertIsNone(self.policy.graphics_result(args))
        data = self.policy.payload(True, True, self.snapshot, 1, result)
        self.assertEqual(data['graphics'], result)
        self.assertEqual(data['effectiveMode'], 'vanilla')
        self.assertFalse(data['lostContactAvailable'])

    def test_graphics_ack_is_owned_by_current_battle_and_cleared_on_stop(self):
        self.settings['tacticalDiagnostics'] = True
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 0, 'svgApi': True, 'glyphCount': 21})
        self.assertIsNone(self.view._graphicsResult)
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1, 'svgApi': True, 'glyphCount': 21})
        self.assertEqual(self.frames[-1]['graphics'], {'svgApi': True, 'glyphCount': 21})
        self.bridge.stop()
        self.assertIsNone(self.view._graphicsResult)
