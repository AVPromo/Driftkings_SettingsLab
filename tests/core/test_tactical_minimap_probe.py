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
        self.cursor_visible = False
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
            'gui.battle_control.minimap_utils': module(MINIMAP_SIZE=(210, 210)),
            'GUI': module(mcursor=lambda: Owner(visible=self.cursor_visible)),
            'Driftkings.views.battle.tactical_minimap': module(presentation_trial_allowed=lambda component: False, native_adapter=factory, native_player_point=lambda component, record: None, native_objective_points=lambda component, records: [], native_circle_points=lambda component, record: [], native_ping_points=lambda component, records: [], native_camera_line=lambda component, record: None, native_yaw_lines=lambda component, record: [], native_strategic_point=lambda component, record: None, forward_native_position_input=lambda component, value: 'diagnostic-replay'),
            'Driftkings.views.hangar.common': module(publish_card=publish),
            'Driftkings.core.hud_visibility': module(hudVisibility=hud)})
        self.bridge = self.api['ProbeBridge'](object(), lambda config: self.settings,
            schedule=lambda delay, fn: self.scheduled.append((delay, fn)) or len(self.scheduled),
            cancel=lambda token: self.cancelled.append(token))
        self.view = Owner(_ready=True, _guiVisible=True, _acknowledged=False, destroy=lambda: None)
        self.bridge.views.add(self.view)
        self.component = Owner(sessionProvider=Owner(), isModalViewShown=lambda: False,
            flashObject=Owner(as_DriftkingsMinimapGeometry=lambda *args: '1|800|400|200|200|1000|800'))

    def test_performance_aggregates_are_bounded_opt_in_and_reset_per_battle(self):
        self.bridge.refresh()
        self.assertEqual(self.bridge._metrics.snapshot()['records'], {})
        reports, ticks = [], [0]
        def clock():
            ticks[0] += 1
            return ticks[0] / 1000.0
        self.bridge._metrics.clock = clock
        self.bridge._metrics.reporter = reports.append
        self.settings['tacticalDiagnostics'] = True
        self.bridge.bind_native(self.component)
        self.bridge.start()
        before = self.bridge._metrics.snapshot()['records']['tactical_minimap.refresh']['calls']
        self.bridge.refresh()
        records = self.bridge._metrics.snapshot()['records']
        self.assertEqual(records['tactical_minimap.refresh']['calls'], before + 1)
        self.assertGreater(records['tactical_minimap.capture']['calls'], 0)
        self.assertGreater(records['tactical_minimap.publish']['calls'], 0)
        self.assertGreater(records['tactical_minimap.geometry']['calls'], 0)
        self.assertGreater(records['tactical_minimap.refresh']['totalMs'], 0)
        self.assertLessEqual(len(records), 16)
        self.assertEqual(reports, [])  # No report for every frame.
        self.bridge.stop()
        self.assertTrue(reports)
        report_count = len(reports)
        self.bridge.stop()
        self.assertEqual(len(reports), report_count)
        self.assertFalse(self.bridge._metrics.enabled)
        calls = self.bridge._metrics.snapshot()['records']['tactical_minimap.refresh']['calls']
        self.bridge.refresh()
        self.assertEqual(self.bridge._metrics.snapshot()['records']['tactical_minimap.refresh']['calls'], calls)
        self.bridge.start()
        self.assertLess(self.bridge._metrics.snapshot()['records']['tactical_minimap.refresh']['calls'], calls)

    def test_performance_counts_unchanged_publications_without_forcing_payload_changes(self):
        self.settings['tacticalDiagnostics'] = True
        frames = []
        def publish(view, data):
            frames.append(data)
            return False
        self.bridge._publish = publish
        self.bridge.start()
        self.bridge.refresh()
        self.assertEqual(frames[-1], frames[-2])
        records = self.bridge._metrics.snapshot()['records']
        self.assertGreater(records['tactical_minimap.skipped']['count'], 0)
        self.assertNotIn('tactical_minimap.published', records)

    def test_presentation_audit_is_bounded_read_only_and_never_grants_replacement(self):
        read = self.policy.presentation_response
        wire = '1|1|0.9|1|1|1|1|1|1|0;entries|flash.display::Sprite|1|1|12|2|0|1'
        result = read(wire)
        self.assertTrue(result['available'])
        self.assertFalse(result['replacementAllowed'])
        self.assertFalse(result['coupledInput'])
        self.assertEqual(result['children'][0]['roles'], 2)
        self.assertEqual(result['children'][0]['className'], 'flash.display::Sprite')
        for value in (None, [], 'x' * 8193, '0|unavailable',
                      wire.replace('0.9', 'NaN'), wire.replace('|12|', '|65536|'),
                      wire.replace('|12|2|', '|12|8|'), wire.replace('entries|', 'bad name|'),
                      wire.replace('|1|1|1|0;', '|1|1|true|0;'), wire + ';extra'):
            self.assertFalse(read(value)['available'])
        self.settings['tacticalDiagnostics'] = True
        calls = []
        self.component.flashObject.as_DriftkingsPresentationAudit = lambda: calls.append(True) or wire
        self.bridge.bind_native(self.component)
        self.bridge._read_geometry()
        self.bridge._read_geometry()
        self.assertEqual(calls, [True])
        self.assertFalse(self.bridge._presentation_audit['replacementAllowed'])
        # Rebind audits the new owner; no audit is repeated every 250ms.
        self.bridge.bind_native(self.component)
        self.assertEqual(calls, [True, True])

    def test_missing_presentation_audit_does_not_invalidate_native_geometry(self):
        self.settings['tacticalDiagnostics'] = True
        self.bridge.bind_native(self.component)
        self.assertTrue(self.bridge._calibration['available'])
        self.assertFalse(self.bridge._presentation_audit['available'])
        self.assertEqual(self.bridge._presentation_audit['reason'], 'presentation-method-unavailable')

    def test_training_trial_is_opt_in_checks_evidence_and_restores_on_stop(self):
        settings = {'tacticalPresentationTrial': True}
        data = dict(enabled=True, acknowledged=True, available=True, playerAvailable=True,
                    mapContext='topography', calibration={'available': True},
                    graphics={'svgApi': True, 'glyphCount': 21})
        audit = dict(available=True, background=True, entries=True, hitArea=True,
                     coupledInput=False, visible=True, alpha=1)
        ready = self.policy.presentation_trial_ready
        self.assertTrue(ready(settings, data, audit))
        self.assertFalse(ready({}, data, audit))
        for key, value in (('enabled', False), ('acknowledged', False), ('available', False),
                           ('playerAvailable', False), ('mapContext', 'classic'),
                           ('calibration', {}), ('graphics', {'svgApi': False, 'glyphCount': 21})):
            self.assertFalse(ready(settings, dict(data, **{key: value}), audit))
        self.assertFalse(ready(settings, data, dict(audit, coupledInput=True)))
        self.bridge._presentation_audit = audit
        calls = []
        self.bridge._native = lambda: self.component
        self.component.flashObject.as_DriftkingsPresentationTrial = lambda action: calls.append(action) or ('active' if action == 'start' else 'restored')
        self.bridge._try_trial(self.component, settings, data)
        self.assertEqual(calls, [])  # Independent native ownership/mode guard.
        self.api['presentation_trial_allowed'] = lambda component: True
        self.bridge._try_trial(self.component, settings, data)
        self.bridge._try_trial(self.component, settings, data)
        self.assertEqual(calls, ['start'])
        self.assertEqual(self.bridge._trial_status, 'active')
        self.bridge.stop()
        self.assertEqual(calls, ['start', 'restore'])
        self.assertEqual(self.bridge._trial_status, 'restored')
        self.bridge.stop()
        self.assertEqual(calls, ['start', 'restore'])

    def test_preferences_publish_separately_without_enabling_replacement(self):
        self.settings.update(tacticalDiagnostics=True, minimapMode='driftkings',
                             tactical={'theme': 'military', 'size': 400})
        self.bridge.start()
        data = self.frames[-1]
        self.assertEqual(data['visualConfig']['theme'], 'military')
        self.assertEqual(data['visualConfig']['size'], 400)
        self.assertEqual(data['rendererSelection']['requestedMode'], 'driftkings')
        self.assertEqual(data['rendererSelection']['effectiveMode'], 'vanilla')
        self.assertTrue(data['rendererSelection']['nativeVisible'])
        self.assertFalse(data['rendererSelection']['rendererVisible'])
        self.assertEqual(self.settings['tactical'], {'theme': 'military', 'size': 400})
        self.settings['tacticalDiagnostics'] = False
        self.assertFalse(self.bridge.enabled())  # Renderer preference does not opt into diagnostics.

    def test_cell_ping_response_rejects_invalid_and_duplicate_samples(self):
        read = self.policy.cell_ping_response
        expected = dict(x=.25, y=.75, kind='cell', state='attack')
        self.assertEqual(read('.25,.75;.25,.75;nan,.5;2,0;bad'), [expected])
        for value in (None, {}, '', 'x' * 4097, 'inf,0', '0,-1'):
            self.assertEqual(read(value), [])
        self.assertEqual(self.policy.ping_points(read('.25,.75')), [expected])
        self.assertLessEqual(len(read(';'.join('%s,0' % (i / 40.0) for i in range(40)))), 32)

    def test_enemy_samples_require_current_visibility_and_strip_identity(self):
        enemy = dict(id=42, name='private', side='enemy', state='visible', visible=True,
                     vehicleClass='mediumTank', x=.3, y=.7)
        geometry = dict(available=True, x=800, y=400, width=200, height=200,
                        stageWidth=1000, stageHeight=800)
        self.snapshot['markers'] = [enemy]
        for enabled, ack in ((False, True), (True, False)):
            self.assertNotIn('enemyPoints', self.policy.payload(enabled, ack, self.snapshot, calibration=geometry))
        data = self.policy.payload(True, True, self.snapshot, calibration=geometry)
        self.assertEqual(data['enemyPoints'], [dict(side='enemy', vehicleClass='mediumTank', x=.3, y=.7)])
        self.assertEqual(data['alliedPoints'], [])
        for changes in ({'visible': False}, {'state': 'lost'}, {'vehicleClass': 'unknown'}, {'x': float('nan')}):
            self.assertEqual(self.policy.enemy_calibration_points([dict(enemy, **changes)]), [])
        self.snapshot['markers'] = []
        self.assertEqual(self.policy.payload(True, True, self.snapshot, calibration=geometry)['enemyPoints'], [])

    def test_wreck_contract_rejects_live_hidden_and_invalid_entries(self):
        wreck = dict(id=42, name='private', side='enemy', state='destroyed', visible=True,
                     vehicleClass='heavyTank', x=.3, y=.7)
        clean = self.policy.destroyed_calibration_points([wreck])
        self.assertEqual(clean, [dict(side='enemy', state='destroyed', vehicleClass='heavyTank', x=.3, y=.7)])
        self.assertEqual(self.policy.enemy_calibration_points([wreck]), [])
        for changes in ({'visible': False}, {'state': 'visible'}, {'side': 'unknown'}, {'x': float('nan')}):
            self.assertEqual(self.policy.destroyed_calibration_points([dict(wreck, **changes)]), [])
        self.assertEqual(self.policy.destroyed_calibration_points([]), [])

    def test_yaw_commands_validate_limits_and_clear_previous_state(self):
        record = {}
        update = self.policy.update_yaw_limits
        update(record, ('setYawLimit', -20, 30))
        self.assertEqual(record['yawLimits'], (-20, 30))
        update(record, ('unrelated',))
        self.assertIn('yawLimits', record)
        update(record, ('clearYawLimit',))
        self.assertNotIn('yawLimits', record)
        for limits in ((float('nan'), 30), (-181, 20), (30, -20), (False, 20), ('-20', 20)):
            update(record, ('setYawLimit', -20, 30))
            update(record, ('setYawLimit',) + limits)
            self.assertNotIn('yawLimits', record)

    def test_yaw_hooks_reuse_personal_entry_and_native_clear_command(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component = Owner()
        original = lambda *args: 7
        hooks['addEntry'](original, component, 'ViewPointEntry', 'personal', object(), True)
        hooks['invoke'](original, component, 8, 'setYawLimit', -20, 30)
        self.assertNotIn('yawLimits', bridge._personal_entries[component])
        hooks['invoke'](original, component, 7, 'setYawLimit', -20, 30)
        self.assertEqual(bridge._personal_entries[component]['yawLimits'], (-20, 30))
        hooks['invoke'](original, component, 7, 'clearYawLimit')
        self.assertNotIn('yawLimits', bridge._personal_entries[component])
        hooks['delEntry'](original, component, 7)
        self.assertNotIn(component, bridge._personal_entries)

    def test_strategic_area_protocol_rejects_malformed_and_degenerate_shapes(self):
        read = self.policy.strategic_area_response
        points = read('0,0;1,0;1,1;0,1')
        self.assertEqual(len(points), 4)
        self.assertEqual(points[2], dict(x=1, y=1))
        self.assertEqual(len(read('-.1,0;1,0;1,1;-.1,1')), 4)
        for value in (None, {}, '', '0,0;1,1', 'nan,0;1,0;1,1;0,1',
                      '0,0;0,0;0,0;0,0', '-5,0;1,0;1,1;0,1', 'x' * 1025):
            self.assertEqual(read(value), [])

    def test_strategic_area_follows_native_visibility_without_previous_frame(self):
        self.settings['tacticalDiagnostics'] = True
        self.api['native_strategic_point'] = lambda component, record: dict(x=.5, y=.5)
        self.component.flashObject.as_DriftkingsStrategicArea = lambda: '0,0;1,0;1,1;0,1'
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.assertEqual(len(self.frames[-1]['strategicArea']), 4)
        self.api['native_strategic_point'] = lambda component, record: None
        self.bridge.refresh()
        self.assertEqual(self.frames[-1]['strategicArea'], [])
        self.api['native_strategic_point'] = lambda component, record: dict(x=.5, y=.5)
        self.component.flashObject.as_DriftkingsStrategicArea = lambda: ''
        self.bridge.refresh()
        self.assertEqual(self.frames[-1]['strategicArea'], [])

    def test_strategic_point_contract_rejects_invalid_and_strips_details(self):
        self.assertEqual(self.policy.strategic_point(dict(x=.3, y=.7, matrix='private')), dict(x=.3, y=.7))
        for value in (None, {}, dict(x=float('nan'), y=0), dict(x=2, y=0)):
            self.assertIsNone(self.policy.strategic_point(value))

    def test_strategic_hooks_track_native_matrix_activation_and_cleanup(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component = Owner()
        original = lambda *args: 7
        hooks['addEntry'](original, component, 'StrategicCameraEntry', 'personal', 'matrix', True)
        record = bridge._strategic_entries[component]
        hooks['setMatrix'](original, component, 7, 'updated')
        self.assertEqual(record['matrix'], 'updated')
        hooks['setActive'](original, component, 7, False)
        self.assertFalse(record['active'])
        hooks['delEntry'](original, component, 7)
        self.assertNotIn(component, bridge._strategic_entries)
        hooks['addEntry'](original, component, 'StrategicCameraEntry', 'personal', 'matrix', True)
        bridge.stop()
        self.assertEqual(len(bridge._strategic_entries), 0)

    def test_gameface_click_dry_run_validates_generation_and_native_pixels(self):
        read = self.policy.gameface_click_sample
        args = dict(protocol=1, generation=3, x=.5, y=.25, button=0)
        value = read(args, 3, 2, (210, 210), 1)
        self.assertEqual((value['localX'], value['localY']), (105, 52.5))
        for changes in ({'generation': 2}, {'protocol': True}, {'x': 2}, {'y': float('nan')}, {'button': False}, {'target': 'unknown'}):
            self.assertIsNone(read(dict(args, **changes), 3, 2, (210, 210), 1))

    def test_gameface_click_round_trip_is_cursor_gated_and_never_dispatches(self):
        self.settings['tacticalDiagnostics'] = True
        self.view._cursorVisible = True
        self.component.getMinimapDimensions = lambda: 10
        self.component.onMinimapClicked = lambda *args: self.fail('Dry run must not invoke native input')
        self.component.flashObject.as_DriftkingsMinimapGeometry = lambda: '1|800|400|200|200|1000|800|2'
        self.bridge.bind_native(self.component)
        self.bridge.start()
        args = dict(protocol=1, generation=1, request=1, x=.5, y=.25, button=0)
        self.bridge.receive_sample_input(self.view, args)
        self.assertIsNone(self.view._sampleInput)
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.bridge.receive_sample_input(self.view, args)
        self.assertIsNone(self.view._sampleInput)  # Native cursor independently checked.
        self.cursor_visible = True
        self.bridge.receive_sample_input(self.view, args)
        self.assertEqual(self.frames[-1]['gamefaceInput']['localX'], 105)
        self.assertEqual(self.frames[-1]['gamefaceInput']['localY'], 52.5)
        self.assertTrue(self.frames[-1]['sampleInputEnabled'])
        self.component.isModalViewShown = lambda: True
        self.bridge.receive_sample_input(self.view, args)
        self.assertEqual(self.view._sampleSequence, 1)
        self.assertFalse(self.bridge.sample_input_enabled(self.view))
        self.component.isModalViewShown = lambda: False
        self.bridge.receive_sample_input(self.view, dict(args, generation=0))
        self.assertEqual(self.view._sampleSequence, 1)
        self.view._cursorVisible = False
        self.bridge.receive_sample_input(self.view, args)
        self.assertEqual(self.view._sampleSequence, 1)
        self.view._cursorVisible = True
        self.bridge.setBattleHudVisible(False)
        self.bridge.receive_sample_input(self.view, args)
        self.assertEqual(self.view._sampleSequence, 1)
        self.bridge.stop()
        self.assertIsNone(self.view._sampleInput)
        self.assertEqual(self.view._sampleSequence, 0)

    def test_input_request_rejects_duplicates_old_and_invalid_identifiers(self):
        read = self.policy.input_request
        self.assertEqual(read({'request': 2}, 1), 2)
        for value in (None, False, 1, 0, -1, float('nan'), 1.5, '2', 2147483648):
            self.assertIsNone(read({'request': value}, 1))

    def test_forwarded_click_commits_request_before_native_reentry_and_uses_fresh_size(self):
        self.settings['tacticalDiagnostics'] = True
        self.cursor_visible = True
        self.view._cursorVisible = True
        self.component.getMinimapDimensions = lambda: 10
        size = [2]
        self.component.flashObject.as_DriftkingsMinimapGeometry = lambda: '1|800|400|200|200|1000|800|' + str(size[0])
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        args = dict(protocol=1, generation=1, request=1, x=.5, y=.25, button=0)
        forwarded = []
        def forward(component, value):
            forwarded.append((component, dict(value)))
            self.bridge.receive_sample_input(self.view, args)
            return 'forwarded'
        self.api['forward_native_position_input'] = forward
        size[0] = 4
        self.bridge.receive_sample_input(self.view, args)
        self.bridge.receive_sample_input(self.view, args)
        self.assertEqual(len(forwarded), 1)
        self.assertEqual(forwarded[0][1]['sizeIndex'], 4)
        self.assertEqual(self.frames[-1]['gamefaceInput']['dispatch'], 'forwarded')
        self.assertEqual(self.frames[-1]['sampleInputRequest'], 1)
        self.bridge.receive_sample_input(self.view, dict(args, request=2, generation=0))
        self.assertEqual(len(forwarded), 1)
        self.bridge.receive_sample_input(self.view, dict(args, request=2, button=1))
        self.bridge.receive_sample_input(self.view, dict(args, request=2, button=1))
        self.assertEqual(len(forwarded), 2)
        self.assertEqual(forwarded[1][1]['button'], 1)
        self.bridge.receive_sample_input(self.view, dict(args, request=3, target='vehicle'))
        self.assertEqual(len(forwarded), 2)
        self.assertEqual(self.frames[-1]['gamefaceInput']['dispatch'], 'diagnostic-vehicle')
        self.bridge.stop()
        self.assertEqual(self.view._sampleRequest, 0)

    def test_native_click_normalization_is_independent_of_visual_size(self):
        read = self.policy.native_click_sample
        self.assertEqual(read(105, 52.5, 0, 5, (210, 210), 1),
                         dict(x=.5, y=.25, button=0, sizeIndex=5, sequence=1))
        self.assertEqual(read(420, 160, 1, 0, (840, 320), 2)['x'], .5)
        for x, y in ((0, 0), (210, 210), (0, 210), (210, 0)):
            self.assertIsNotNone(read(x, y, 0, 0, (210, 210), 1))
        for args in ((-1, 0, 0, 0, (210, 210), 1), (0, 211, 0, 0, (210, 210), 1),
                     (0, 0, False, 0, (210, 210), 1), (0, 0, 0, 6, (210, 210), 1),
                     (0, 0, 0, 0, (0, 210), 1), (0, 0, 0, 0, (210, 210), 0),
                     (float('nan'), 0, 0, 0, (210, 210), 1)):
            self.assertIsNone(read(*args))

    def test_click_observation_requires_current_battle_and_clears_on_stop(self):
        self.settings['tacticalDiagnostics'] = True
        self.component.getMinimapDimensions = lambda: 10
        self.bridge.bind_native(self.component)
        self.bridge.observe_native_click(self.component, 105, 105, 0, 2)
        self.assertIsNone(self.bridge._last_input)
        self.bridge.start()
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.bridge.observe_native_click(self.component, 105, 105, 0, 2)
        self.assertEqual(self.frames[-1]['nativeInput'], dict(x=.5, y=.5, button=0, sizeIndex=2, sequence=1))
        self.bridge.observe_native_click(Owner(), 0, 0, 0, 2)
        self.assertEqual(self.bridge._last_input['sequence'], 1)
        self.bridge.setBattleHudVisible(False)
        self.bridge.observe_native_click(self.component, 0, 0, 0, 2)
        self.assertEqual(self.bridge._last_input['sequence'], 1)
        self.bridge.setBattleHudVisible(True)
        self.bridge.observe_native_click(self.component, 210, 210, 1, 5)
        self.assertEqual(self.frames[-1]['nativeInput']['sequence'], 2)
        self.bridge.stop()
        self.assertIsNone(self.bridge._last_input)
        self.assertEqual(self.bridge._input_sequence, 0)

    def test_geometry_optional_size_index_preserves_legacy_protocol(self):
        read = self.policy.geometry_response
        old = '1|800|400|200|200|1000|800'
        self.assertTrue(read(old)['available'])
        self.assertNotIn('sizeIndex', read(old))
        self.assertEqual(read(old + '|5')['sizeIndex'], 5)
        self.assertNotIn('sizeIndex', read(old + '|6'))
        self.assertNotIn('sizeIndex', read(old + '|nan'))

    def test_native_click_hook_preserves_original_call_result_and_failure(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        calls, observed = [], []
        component, token = Owner(), object()
        def original(*args):
            calls.append(args)
            return token
        bridge.observe_native_click = lambda *args: observed.append((len(calls), args))
        args = (component, 105, 105, 0, 2)
        self.assertIs(hooks['onMinimapClicked'](original, *args), token)
        self.assertEqual(calls, [args])
        self.assertEqual(observed, [(1, args)])
        def broken_observer(*args):
            raise RuntimeError('Simulated diagnostic failure')
        bridge.observe_native_click = broken_observer
        self.assertIs(hooks['onMinimapClicked'](original, *args), token)
        self.assertEqual(len(calls), 2)
        def broken_original(*args):
            raise RuntimeError('Native failure must propagate')
        with self.assertRaises(RuntimeError):
            hooks['onMinimapClicked'](broken_original, *args)

    def test_camera_contract_is_bounded_and_removes_private_fields(self):
        value = dict(x=.5, y=.5, x2=1, y2=.5)
        self.assertEqual(self.policy.camera_line(dict(value, matrix='private')), value)
        for invalid in (None, {}, dict(value, x2=float('nan')), dict(value, y=-1)):
            self.assertIsNone(self.policy.camera_line(invalid))

    def test_camera_hooks_follow_visibility_matrix_and_disposal(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component, provider = Owner(), object()
        original = lambda *args: 7
        hooks['addEntry'](original, component, 'ArcadeCameraEntry', 'personal', provider, True)
        record = bridge._camera_entries[component]
        self.assertFalse(record['direction'])
        hooks['invoke'](original, component, 7, 'showDirectionLine')
        self.assertTrue(record['direction'])
        hooks['setMatrix'](original, component, 7, 'new-provider')
        self.assertEqual(record['matrix'], 'new-provider')
        hooks['invoke'](original, component, 7, 'hideDirectionLine')
        self.assertFalse(record['direction'])
        hooks['setActive'](original, component, 7, False)
        self.assertFalse(record['active'])
        hooks['delEntry'](original, component, 7)
        self.assertNotIn(component, bridge._camera_entries)
        hooks['addEntry'](original, component, 'ArcadeCameraEntry', 'personal', provider, True)
        bridge.stop()
        self.assertEqual(len(bridge._camera_entries), 0)

    def test_vehicle_labels_are_bounded_text_and_follow_current_publication(self):
        label = self.policy.vehicle_label
        self.assertEqual(label(u'  KV-2\n\x00  '), u'KV-2')
        self.assertEqual(label(None), u'')
        self.assertEqual(len(label('x' * 1000)), 64)
        enemy = dict(side='enemy', visible=True, state='visible', vehicleClass='heavyTank',
                     x=.5, y=.5, vehicleLabel=u'T-34-85', name='private', id=42)
        result = self.policy.enemy_calibration_points([enemy])[0]
        self.assertEqual(result['label'], u'T-34-85')
        self.assertNotIn('name', result)
        self.assertNotIn('id', result)
        self.assertEqual(self.policy.enemy_calibration_points([dict(enemy, visible=False)]), [])
        self.assertEqual(self.policy.enemy_calibration_points([]), [])

    def test_training_hints_are_separate_from_spotted_enemies_and_mode_gated(self):
        hint = dict(side='training', visible=True, state='training', vehicleClass='heavyTank',
                    x=.5, y=.5, vehicleLabel='Training tank', goal=True, id=101)
        geometry = dict(available=True, x=800, y=400, width=200, height=200,
                        stageWidth=1000, stageHeight=800)
        self.snapshot['trainingMarkers'] = [hint]
        self.assertEqual(self.policy.payload(True, True, self.snapshot, calibration=geometry)['trainingPoints'], [])
        self.snapshot['context'] = 'topography'
        data = self.policy.payload(True, True, self.snapshot, calibration=geometry)
        self.assertEqual(len(data['trainingPoints']), 1)
        self.assertTrue(data['trainingPoints'][0]['goal'])
        self.assertNotIn('id', data['trainingPoints'][0])
        self.assertEqual(self.policy.enemy_calibration_points([hint]), [])
        self.assertEqual(self.policy.training_calibration_points([dict(hint, visible=False)]), [])
        self.assertEqual(self.policy.training_calibration_points([]), [])
        self.assertNotIn('trainingPoints', self.policy.payload(True, False, self.snapshot, calibration=geometry))

    def test_artillery_ping_uses_native_aim_area_symbol(self):
        self.assertEqual(self.policy.PING_SYMBOLS['ArtyMarkerMinimapEntry'], 'artillery')
        value = dict(kind='artillery', x=.4, y=.6, state='attack', sender='private')
        self.assertEqual(self.policy.ping_points([value]),
                         [dict(kind='artillery', x=.4, y=.6, state='attack')])

    def test_cell_flashes_follow_current_native_frame_without_history(self):
        self.settings['tacticalDiagnostics'] = True
        self.component.getMinimapDimensions = lambda: 10
        self.component.flashObject.as_DriftkingsCellPings = lambda: '.25,.75'
        self.bridge.bind_native(self.component)
        self.bridge.start()
        self.bridge.acknowledge(self.view, {'protocol': 1, 'generation': 1})
        self.assertEqual(self.frames[-1]['pings'][0]['kind'], 'cell')
        self.component.flashObject.as_DriftkingsCellPings = lambda: ''
        self.bridge.refresh()
        self.assertEqual(self.frames[-1]['pings'], [])
        self.component.flashObject.as_DriftkingsCellPings = lambda: '.25,.75'
        self.component.getMinimapDimensions = lambda: 12
        self.bridge.refresh()
        self.assertEqual(self.frames[-1]['pings'], [])

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

    def test_native_circle_commands_add_update_remove_and_clear(self):
        record = {'circles': {}}
        self.policy.update_ranges(record, ('as_addDynamicViewRange', 0x67cf69, 50, 400))
        self.assertEqual(record['circles']['view'], {'color': '#67cf69', 'alpha': .5, 'radius': 400})
        self.policy.update_ranges(record, ('as_updateDynRange', 450))
        self.assertEqual(record['circles']['view']['radius'], 450)
        self.policy.update_ranges(record, ('as_delDynRange',))
        self.assertEqual(record['circles'], {})
        for method in self.policy.RANGE_ADD:
            self.policy.update_ranges(record, (method, 0xffffff, 100, 50))
        self.assertEqual(len(record['circles']), 4)
        self.policy.update_ranges(record, ('as_removeAllCircles',))
        self.assertEqual(record['circles'], {})
        self.policy.update_ranges(record, ('as_addDrawRange', 0, 101, float('nan')))
        self.assertEqual(record['circles'], {})

    def test_circle_contract_rejects_invalid_values_and_strips_radius(self):
        value = dict(kind='view', x=.5, y=.5, rx=.4, ry=.2, alpha=.5, color='#ffffff', radius=400)
        self.assertNotIn('radius', self.policy.circle_points([value])[0])
        self.assertEqual(len(self.policy.circle_points([value, value])), 1)
        self.assertEqual(self.policy.circle_points([dict(value, rx=float('nan'))]), [])
        self.assertEqual(self.policy.circle_points([dict(value, alpha=0)]), [])

    def test_circle_publication_tracks_native_entry_and_lifecycle(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component, provider = Owner(), object()
        original = lambda *args: 7
        hooks['addEntry'](original, component, 'ViewRangeCirclesEntry', 'personal', provider, True)
        hooks['invoke'](original, component, 7, 'as_addDrawRange', 0xffffff, 50, 500)
        self.assertEqual(bridge._circle_entries[component]['circles']['draw']['radius'], 500)
        hooks['setActive'](original, component, 7, False)
        self.assertFalse(bridge._circle_entries[component]['active'])
        hooks['delEntry'](original, component, 7)
        self.assertNotIn(component, bridge._circle_entries)
        hooks['addEntry'](original, component, 'ViewRangeCirclesEntry', 'personal', provider, True)
        bridge.stop()
        self.assertEqual(len(bridge._circle_entries), 0)

    def test_ping_publication_response_deactivation_and_native_expiry(self):
        self.settings['tacticalDiagnostics'] = True
        bridge, hooks, events = self.install_runtime_stubs()
        bridge.install()
        component, provider = Owner(), object()
        original = lambda *args: 9
        hooks['addEntry'](original, component, 'MarkAttentionEntryUI', 'equipments', provider, True)
        self.assertEqual(bridge._ping_entries[component][9]['kind'], 'attention')
        hooks['invoke'](original, component, 9, 'setState', 'reply')
        self.assertEqual(bridge._ping_entries[component][9]['state'], 'reply')
        hooks['setActive'](original, component, 9, False)
        self.assertFalse(bridge._ping_entries[component][9]['active'])
        hooks['delEntry'](original, component, 9)
        self.assertEqual(bridge._ping_entries[component], {})
        hooks['addEntry'](original, component, 'UnspottedMarkerUI', 'equipments', provider, True)
        self.assertEqual(bridge._ping_entries[component], {})
        hooks['addEntry'](original, component, 'MarkGoingToPositionEntryUI', 'equipments', provider, True)
        hooks['addEntry'](original, component, 'ArtyMarkerMinimapEntry', 'equipments', provider, True)
        self.assertEqual(bridge._ping_entries[component][9]['kind'], 'artillery')
        hooks['delEntry'](original, component, 9)
        self.assertEqual(bridge._ping_entries[component], {})
        hooks['addEntry'](original, component, 'ArtyHitDotMarkerUI', 'equipments', provider, True)
        self.assertEqual(bridge._ping_entries[component], {})
        hooks['addEntry'](original, component, 'ArtyHitDotMarkerUI', 'personal', provider, True)
        self.assertEqual(bridge._ping_entries[component][9]['kind'], 'artilleryImpact')
        hooks['delEntry'](original, component, 9)
        self.assertEqual(bridge._ping_entries[component], {})
        bridge.stop()
        self.assertEqual(len(bridge._ping_entries), 0)

    def test_ping_contract_is_bounded_and_contains_no_sender_or_text(self):
        value = dict(kind='going', x=.5, y=.25, state='reply', sender=666, text='private')
        clean = self.policy.ping_points([value])[0]
        self.assertEqual(clean, {'kind': 'going', 'x': .5, 'y': .25, 'state': 'reply'})
        self.assertEqual(len(self.policy.ping_points([value] * 40)), 32)
        self.assertEqual(self.policy.ping_points([dict(value, kind='unspotted')]), [])
        self.assertEqual(self.policy.ping_points([dict(value, x=float('inf'))]), [])
        self.assertEqual(self.policy.ping_points([dict(value, state='unknown')]), [])

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
            'GUI': module(mcursor=lambda: Owner(visible=fixture.cursor_visible)),
            'Driftkings.views.battle.tactical_minimap': module(presentation_trial_allowed=lambda component: False, native_adapter=lambda *args: None, native_player_point=lambda component, record: None, native_objective_points=lambda component, records: [], native_circle_points=lambda component, record: [], native_ping_points=lambda component, records: [], native_camera_line=lambda component, record: None, native_yaw_lines=lambda component, record: [], native_strategic_point=lambda component, record: None, forward_native_position_input=lambda component, value: 'diagnostic-replay'),
            'Driftkings.views.hangar.common': module(publish_card=lambda *args: None),
            'frameworks.wulf': module(ViewModel=BaseModel),
            'gui.impl.pub.view_component': module(ViewComponent=BaseView),
            'gui.impl.battle.random.hud': module(RandomHUDView=NativeHUD),
            'gui.Scaleform.daapi.view.battle.shared.minimap.component': module(MinimapComponent=NativeMap),
            'gui.shared': module(events=module(GameEvent=module(GUI_VISIBILITY=1, SHOW_CURSOR=2, HIDE_CURSOR=3)), EVENT_BUS_SCOPE=module(BATTLE=2, GLOBAL=3)),
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
        self.assertEqual(len(hooks), 9)
        self.assertEqual(len(events), 4)
        native = {7: object()}
        children = hooks['_getChildComponents'](lambda parent: native, Owner())
        self.assertIs(children[7], native[7])
        self.assertNotIn(123, native)
        self.assertIn(123, children)
        view = children[123]()
        self.assertIsNotNone(view)
        self.assertEqual(view.model.sizes, {'properties': 3, 'commands': 2})
        self.assertEqual(len(view._getEvents()), 2)
        self.assertEqual(len(view._getListeners()), 3)
        view._showCursor(None)
        self.assertTrue(view._cursorVisible)
        view._hideCursor(None)
        self.assertFalse(view._cursorVisible)
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
