# -*- coding: utf-8 -*-
import gc
import weakref

from support import RuntimeTest, module, source


class Owner(object):
    def __init__(self, **values):
        self.__dict__.update(values)


class NativeAdapterTests(RuntimeTest):
    def setUp(self):
        super(NativeAdapterTests, self).setUp()
        self.api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap')})
        self.reads = []
        def position(provider):
            self.reads.append(provider)
            return provider
        self.plugin = module(_entries={})
        self.component = Owner(getBoundingBox=lambda: ((-100, -200), (300, 600)),
                                getPlugin=lambda name: self.plugin)
        self.dp = module(isSquadMan=lambda vID: vID == 2,
                         getVehicleInfo=lambda vehicle_id: module(getDisplayedName=lambda: u'Test'))
        self.arena_type = module(getMinimapTexture=lambda: 'spaces/test/minimap.dds')
        self.session = Owner(arenaVisitor=module(type=self.arena_type), getArenaDP=lambda: self.dp)
        self.adapter = self.api['NativeMinimapAdapter'](self.component, self.session, position, 1, (210, 210))

    def entry(self, active=True, alive=True, aoi=True, location=1, enemy=True, matrix=(100, 200)):
        return module(isActive=lambda: active, isAlive=lambda: alive, isInAoI=lambda: aoi,
                      getLocation=lambda: location, isEnemy=lambda: enemy,
                      getClassTag=lambda: 'mediumTank', getMatrix=lambda: matrix)

    def test_native_map_and_visible_entries_are_read_without_orientation_or_world_reads(self):
        self.plugin._entries = {1: self.entry(), 2: self.entry(enemy=False)}
        frame = self.adapter.capture()
        self.assertTrue(frame['available'])
        self.assertTrue(frame['partial'])
        self.assertFalse(frame['nativePresentationChanged'])
        self.assertEqual(frame['source'], 'native-minimap-audit')
        self.assertEqual(frame['texture'], 'spaces/test/minimap.dds')
        rows = dict((row['id'], row) for row in frame['markers'])
        self.assertEqual((rows[1]['x'], rows[1]['y']), (.5, .5))
        self.assertEqual(rows[1]['side'], 'enemy')
        self.assertEqual(rows[1]['vehicleLabel'], u'Test')
        self.assertEqual(rows[2]['side'], 'platoon')
        self.assertNotIn('heading', rows[1])
        self.assertFalse(frame['lostContactAvailable'])

    def test_player_relation_uses_native_id_and_never_relabels_an_enemy(self):
        self.dp.getPlayerVehicleID = lambda: 2
        self.plugin._entries = {1: self.entry(enemy=False), 2: self.entry(enemy=False)}
        rows = dict((row['id'], row) for row in self.adapter.capture()['markers'])
        self.assertEqual(rows[1]['side'], 'ally')
        self.assertEqual(rows[2]['side'], 'player')
        self.plugin._entries[2] = self.entry(enemy=True)
        self.assertEqual(dict((row['id'], row['side']) for row in self.adapter.capture()['markers'])[2], 'enemy')

    def test_personal_marker_gate_rejects_dead_observer_and_spectated_vehicle(self):
        Personal = type('Personal', (object,), {
            '__module__': 'gui.Scaleform.daapi.view.battle.shared.minimap.plugins'})
        personal = Personal()
        personal._ctrlVehicleID = 2
        personal._getPlayerVehicleID = lambda: 2
        alive, observer = [True], [False]
        self.dp.getPlayerVehicleID = lambda: 2
        self.dp.getVehicleInfo = lambda vehicle_id: Owner(isAlive=lambda: alive[0], isObserver=lambda: observer[0])
        self.component.sessionProvider = self.session
        self.component.getPlugin = lambda name: personal
        self.assertTrue(self.api['owns_player_marker'](self.component))
        alive[0] = False
        self.assertFalse(self.api['owns_player_marker'](self.component))
        alive[0], observer[0] = True, True
        self.assertFalse(self.api['owns_player_marker'](self.component))
        observer[0] = False
        personal._ctrlVehicleID = 3
        self.assertFalse(self.api['owns_player_marker'](self.component))
        # Native initControlMode creates personal entries while the control ID is 0.
        personal._ctrlVehicleID = 0
        personal._isInPostmortemMode = lambda: False
        personal._isInVideoMode = lambda: False
        personal._isInFreeCamMode = lambda: False
        self.assertTrue(self.api['owns_player_marker'](self.component))
        for name in ('_isInPostmortemMode', '_isInVideoMode', '_isInFreeCamMode'):
            setattr(personal, name, lambda: True)
            self.assertFalse(self.api['owns_player_marker'](self.component))
            setattr(personal, name, lambda: False)
        alive[0] = False
        self.assertFalse(self.api['owns_player_marker'](self.component))
        alive[0], observer[0] = True, True
        self.assertFalse(self.api['owns_player_marker'](self.component))
        observer[0] = False
        personal._ctrlVehicleID = None
        self.assertFalse(self.api['owns_player_marker'](self.component))

    def test_published_far_allies_remain_but_far_enemies_never_read_matrices(self):
        self.plugin._entries = {1: self.entry(enemy=False, aoi=False, location=2)}
        self.assertEqual(len(self.adapter.capture()['markers']), 1)
        self.plugin._entries[1] = self.entry(enemy=True, aoi=False, location=2)
        self.reads[:] = []
        self.assertEqual(self.adapter.capture()['markers'], [])
        self.assertEqual(self.reads, [])

    def test_enemy_disappears_without_reading_or_retaining_previous_matrix(self):
        self.plugin._entries = {1: self.entry(enemy=True)}
        self.assertEqual(len(self.adapter.capture()['markers']), 1)
        for changes in ({'active': False}, {'aoi': False}, {'location': 0}, {'location': 3}):
            self.plugin._entries[1] = self.entry(enemy=True, **changes)
            self.reads[:] = []
            self.assertEqual(self.adapter.capture()['markers'], [])
            self.assertEqual(self.reads, [])

    def test_spotted_far_enemy_is_published_then_removed_when_hidden(self):
        self.plugin._entries = {1: self.entry(enemy=True, aoi=True, location=2)}
        points = self.adapter.capture()['markers']
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0]['side'], 'enemy')
        self.assertEqual((points[0]['x'], points[0]['y']), (.5, .5))
        self.plugin._entries[1] = self.entry(enemy=True, aoi=False, location=0)
        self.reads[:] = []
        self.assertEqual(self.adapter.capture()['markers'], [])
        self.assertEqual(self.reads, [])

    def test_native_wreck_publication_and_expiry_have_no_local_history(self):
        self.plugin._entries = {1: self.entry(enemy=True, alive=False)}
        frame = self.adapter.capture()
        self.assertEqual(frame['markers'], [])
        self.assertEqual(frame['destroyedMarkers'][0]['state'], 'destroyed')
        self.assertEqual(frame['destroyedMarkers'][0]['side'], 'enemy')
        for changes in ({'active': False}, {'aoi': False}, {'location': 0}, {'location': 3}):
            self.plugin._entries[1] = self.entry(enemy=True, alive=False, **changes)
            self.reads[:] = []
            self.assertEqual(self.adapter.capture()['destroyedMarkers'], [])
            self.assertEqual(self.reads, [])
        self.plugin._entries = {}
        self.assertEqual(self.adapter.capture()['destroyedMarkers'], [])

    def test_personal_matrix_uses_world_bounds_and_yaw_not_flash_pixels(self):
        from math import pi
        Personal = type('Personal', (object,), {
            '__module__': 'gui.Scaleform.daapi.view.battle.shared.minimap.plugins'})
        personal = Personal()
        personal._ctrlVehicleID = 2
        personal._getPlayerVehicleID = lambda: 2
        personal._getViewPointID = lambda: 99
        self.dp.getPlayerVehicleID = lambda: 2
        self.dp.getVehicleInfo = lambda vehicle_id: Owner(isAlive=lambda: True, isObserver=lambda: False)
        self.component.sessionProvider = self.session
        self.component.getPlugin = lambda name: personal
        providers = []
        def matrix(provider):
            providers.append(provider)
            return Owner(translation=Owner(x=100, z=200), yaw=pi / 2)
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=matrix),
            'gui.battle_control.minimap_utils': module(getCellIdFromPosition=lambda *args: 54,
                                                       getCellName=lambda *args: 'E6')})
        record = {'id': 99, 'matrix': object(), 'active': True}
        point = api['native_player_point'](self.component, record)
        self.assertEqual((point['x'], point['y'], point['heading']), (.5, .5, 90))
        self.assertEqual(point['cell'], 'E6')
        record['active'] = False
        self.assertIsNone(api['native_player_point'](self.component, record))
        self.assertEqual(len(providers), 1)
        record['active'], record['id'] = True, 100
        self.assertIsNone(api['native_player_point'](self.component, record))
        self.assertEqual(len(providers), 1)

    def test_camera_line_uses_selected_published_matrix_and_rectangular_bounds(self):
        from math import pi
        yaw, reads = [0], []
        selected = [7]
        self.component.getPlugin = lambda name: Owner(_getCameraIDs=lambda: {'ArcadeCameraEntry': 7},
                                                     _getSelectedCameraID=lambda: selected[0])
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=lambda provider: reads.append(provider) or Owner(
                translation=Owner(x=100, z=200), yaw=yaw[0]))})
        api['owns_player_marker'] = lambda component: True
        record = dict(id=7, active=True, direction=True, matrix=object())
        line = api['native_camera_line'](self.component, record)
        self.assertEqual(line, dict(x=.5, y=.5, x2=.5, y2=0))
        yaw[0] = pi / 2
        line = api['native_camera_line'](self.component, record)
        self.assertAlmostEqual(line['x2'], 1)
        self.assertAlmostEqual(line['y2'], .5)
        yaw[0] = pi / 4
        line = api['native_camera_line'](self.component, record)
        self.assertAlmostEqual(line['x2'], 1)
        self.assertAlmostEqual(line['y2'], .25)
        for changes in ({'active': False}, {'direction': False}, {'id': 8}, {'matrix': None}):
            reads[:] = []
            self.assertIsNone(api['native_camera_line'](self.component, dict(record, **changes)))
            self.assertEqual(reads, [])
        selected[0] = 8
        self.assertIsNone(api['native_camera_line'](self.component, record))
        selected[0] = 7
        api['owns_player_marker'] = lambda component: False
        self.assertIsNone(api['native_camera_line'](self.component, record))

    def test_yaw_limits_follow_hull_matrix_and_native_entry_ownership(self):
        from math import pi
        yaw, reads = [0], []
        self.component.getPlugin = lambda name: Owner(_getViewPointID=lambda: 7)
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=lambda provider: reads.append(provider) or Owner(
                translation=Owner(x=100, z=200), yaw=yaw[0]))})
        api['owns_player_marker'] = lambda component: True
        record = dict(id=7, active=True, matrix=object(), yawLimits=(-45, 45))
        lines = api['native_yaw_lines'](self.component, record)
        self.assertAlmostEqual(lines[0]['x2'], 0)
        self.assertAlmostEqual(lines[0]['y2'], .25)
        self.assertAlmostEqual(lines[1]['x2'], 1)
        self.assertAlmostEqual(lines[1]['y2'], .25)
        yaw[0] = pi
        lines = api['native_yaw_lines'](self.component, record)
        self.assertAlmostEqual(lines[0]['y2'], .75)
        for changes in ({'active': False}, {'id': 8}, {'yawLimits': None}, {'matrix': None}):
            reads[:] = []
            self.assertEqual(api['native_yaw_lines'](self.component, dict(record, **changes)), [])
            self.assertEqual(reads, [])
        api['owns_player_marker'] = lambda component: False
        self.assertEqual(api['native_yaw_lines'](self.component, record), [])

    def test_strategic_aim_uses_selected_published_matrix_only_in_arty_modes(self):
        reads, selected, strategic, arty = [], [7], [True], [False]
        self.component.getPlugin = lambda name: Owner(_getCameraIDs=lambda: {'StrategicCameraEntry': 7},
            _getSelectedCameraID=lambda: selected[0], _isInStrategicMode=lambda: strategic[0],
            _isInArtyMode=lambda: arty[0])
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=lambda provider: reads.append(provider) or Owner(translation=Owner(x=100, z=200)))})
        api['owns_player_marker'] = lambda component: True
        record = dict(id=7, active=True, matrix=object())
        self.assertEqual(api['native_strategic_point'](self.component, record), dict(x=.5, y=.5))
        strategic[0], arty[0] = False, True
        self.assertIsNotNone(api['native_strategic_point'](self.component, record))
        strategic[0], arty[0] = False, False
        reads[:] = []
        self.assertIsNone(api['native_strategic_point'](self.component, record))
        self.assertEqual(reads, [])
        strategic[0] = True
        for changes in ({'active': False}, {'id': 8}, {'matrix': None}):
            self.assertIsNone(api['native_strategic_point'](self.component, dict(record, **changes)))
        selected[0] = 8
        self.assertIsNone(api['native_strategic_point'](self.component, record))
        selected[0] = 7
        api['owns_player_marker'] = lambda component: False
        self.assertIsNone(api['native_strategic_point'](self.component, record))

    def test_position_input_delegates_once_only_to_stock_classic_plugin(self):
        Ping = type('ClassicMinimapPingPlugin', (object,), {
            '__module__': 'gui.Scaleform.daapi.view.battle.classic.minimap'})
        plugin, modal, calls = [Ping()], [False], []
        replay = Owner(isPlaying=False)
        common = module(xvmInstalled=False)
        self.component.getMinimapDimensions = lambda: 10
        self.component.getPlugin = lambda name: plugin[0] if name == 'pinging' else None
        self.component.isModalViewShown = lambda: modal[0]
        self.component.onMinimapClicked = lambda *args: calls.append(args)
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Driftkings.core.tactical_minimap_probe': self.load('core.tactical_minimap_probe'),
            'Driftkings.common': common, 'BattleReplay': module(g_replayCtrl=replay),
            'gui.battle_control.minimap_utils': module(MINIMAP_SIZE=(210, 210))})
        send = api['forward_native_position_input']
        value = dict(x=.5, y=.25, button=0, sizeIndex=4, sequence=1)
        self.assertEqual(send(self.component, value), 'forwarded')
        self.assertEqual(calls, [(105, 52.5, 0, 4)])
        self.assertEqual(send(self.component, dict(value, button=1)), 'forwarded')
        self.assertEqual(calls[-1], (105, 52.5, 1, 4))
        calls[:] = []
        self.assertEqual(send(self.component, dict(value, target='vehicle')), 'diagnostic-vehicle')
        self.assertEqual(calls, [])
        self.assertEqual(send(self.component, dict(value, button=2)), 'diagnostic-button')
        self.assertEqual(send(self.component, dict(value, x=2)), 'invalid-input')
        replay.isPlaying = True
        self.assertEqual(send(self.component, value), 'diagnostic-replay')
        self.assertEqual(send(self.component, dict(value, button=1)), 'diagnostic-replay')
        replay.isPlaying = False
        modal[0] = True
        self.assertEqual(send(self.component, value), 'modal-view')
        modal[0] = False
        common.xvmInstalled = True
        self.assertEqual(send(self.component, value), 'third-party-owner')
        common.xvmInstalled = False
        plugin[0] = Owner()
        self.assertEqual(send(self.component, value), 'third-party-owner')
        plugin[0] = None
        self.assertEqual(send(self.component, value), 'native-input-unavailable')
        self.assertEqual(calls, [])
        plugin[0] = Ping()
        def broken(*args):
            calls.append(args)
            raise RuntimeError('Simulated native failure')
        self.component.onMinimapClicked = broken
        self.assertEqual(send(self.component, value), 'failed')
        self.assertEqual(len(calls), 1)

    def test_native_objectives_read_only_active_publication_and_world_bounds(self):
        reads = []
        def matrix(provider):
            reads.append(provider)
            return Owner(translation=Owner(x=100, z=200))
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=matrix)})
        provider = object()
        records = {1: dict(active=True, matrix=provider, kind='allyBase'),
                   2: dict(active=False, matrix=object(), kind='enemyBase')}
        self.assertEqual(api['native_objective_points'](self.component, records),
                         [{'kind': 'allyBase', 'x': .5, 'y': .5}])
        self.assertEqual(reads, [provider])
        records.clear()
        self.assertEqual(api['native_objective_points'](self.component, records), [])

    def test_capture_controller_state_progress_reset_and_neutral_teams(self):
        states, captured = {}, set()
        Controller = type('Controller', (object,), {
            '__module__': 'gui.battle_control.controllers.team_bases_ctrl',
            'isTeamBaseCaptured': lambda ctrl, client_id: client_id in captured,
            '_getPoints': lambda ctrl, client_id: states[client_id]})
        self.component.sessionProvider = self.session
        self.session.shared = Owner(teamBases=Controller())
        self.dp.getNumberOfTeam = lambda: 1
        self.arena_type.getTeamBasePositionsIterator = lambda: iter([(1, (100, 0, 200), 1)])
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'gui.battle_control.controllers.team_bases_ctrl': module(
                makeClientTeamBaseID=lambda team, number: (number << 6) + team,
                _AVAILABLE_TEAMS_NUMBERS=(1, 2))})
        record = dict(kind='allyBase', number=1)
        position = Owner(x=100, z=200)
        read = lambda: api['native_objective_capture'](self.component, record, position)
        self.assertEqual(read(), {'state': 'idle', 'progress': 0})
        states[65] = (42, 30, 1, False)
        self.assertEqual(read(), {'state': 'capturing', 'progress': 42})
        states[65] = (42, 30, 1, True)
        self.assertEqual(read(), {'state': 'blocked', 'progress': 42})
        captured.add(65)
        self.assertEqual(read(), {'state': 'captured', 'progress': 100})
        states.clear()
        captured.clear()
        self.assertEqual(read(), {'state': 'idle', 'progress': 0})
        record['kind'] = 'controlPoint'
        states[66] = (75, 10, 1, False)
        self.assertEqual(read(), {'state': 'capturing', 'progress': 75})
        record['kind'], record['number'] = 'allyBase', 9
        self.assertEqual(read(), {'state': 'unknown'})

    def test_circle_world_radius_uses_both_dimensions_and_respects_native_active(self):
        reads = []
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=lambda provider: reads.append(provider) or Owner(translation=Owner(x=100, z=200)))})
        record = dict(active=True, matrix=object(), circles={'view': dict(radius=100, color='#ffffff', alpha=.5)})
        value = api['native_circle_points'](self.component, record)[0]
        self.assertEqual((value['x'], value['y'], value['rx'], value['ry']), (.5, .5, .25, .125))
        record['active'] = False
        self.assertEqual(api['native_circle_points'](self.component, record), [])
        self.assertEqual(len(reads), 1)

    def test_ping_matrix_normalization_and_removal_use_current_publication(self):
        reads = []
        api = source('views/battle/tactical_minimap.py', {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Math': module(Matrix=lambda provider: reads.append(provider) or Owner(translation=Owner(x=100, z=200)))})
        records = {1: dict(active=True, matrix=object(), kind='attention', state='attack')}
        self.assertEqual(api['native_ping_points'](self.component, records),
                         [{'x': .5, 'y': .5, 'kind': 'attention', 'state': 'attack'}])
        records[1]['active'] = False
        self.assertEqual(api['native_ping_points'](self.component, records), [])
        self.assertEqual(len(reads), 1)
        records.clear()
        self.assertEqual(api['native_ping_points'](self.component, records), [])

    def test_hidden_lost_transitional_dead_and_inactive_entries_never_read_matrices(self):
        entries = [self.entry(active=False), self.entry(alive=False, active=False), self.entry(aoi=False),
                   self.entry(location=0), self.entry(location=2, aoi=False), self.entry(location=3)]
        def forbidden():
            self.reads.append('forbidden')
            self.fail('Must not read a matrix for an unpublished entry')
        for entry in entries:
            entry.getMatrix = forbidden
        self.plugin._entries = dict(enumerate(entries))
        frame = self.adapter.capture()
        self.assertEqual(frame['markers'], [])
        self.assertEqual(self.reads, [])
        self.assertEqual(frame['entryAudit']['unpublished'], len(entries))

    def test_snapshot_does_not_retain_positions_after_native_entry_disappears(self):
        self.plugin._entries = {1: self.entry()}
        self.assertEqual(len(self.adapter.capture()['markers']), 1)
        self.plugin._entries.clear()
        self.assertEqual(self.adapter.capture()['markers'], [])

    def test_expired_one_entry_does_not_break_other_entries(self):
        bad = self.entry()
        def expired():
            raise ReferenceError('Native entry destroyed')
        bad.getMatrix = expired
        self.plugin._entries = {1: bad, 2: self.entry()}
        self.assertEqual([row['id'] for row in self.adapter.capture()['markers']], [2])

    def test_missing_native_contract_returns_safe_status_without_payload(self):
        self.arena_type.getMinimapTexture = lambda: ''
        frame = self.adapter.capture()
        self.assertFalse(frame['available'])
        self.assertEqual(frame['reason'], 'native-contract-unavailable')
        self.assertFalse(frame['nativePresentationChanged'])
        self.assertEqual(frame['markers'], [])
        self.assertNotIn('texture', frame)

    def test_close_is_idempotent_and_does_not_keep_native_owners_alive(self):
        owner = weakref.ref(self.component)
        del self.component
        gc.collect()
        self.assertIsNone(owner())
        self.assertEqual(self.adapter.capture()['reason'], 'native-owner-unavailable')
        self.adapter.close()
        self.adapter.close()
        self.assertEqual(self.adapter.capture()['reason'], 'adapter-closed')

    def test_factory_rejects_unverified_plugin_before_importing_game_modules(self):
        with self.assertRaises(ValueError):
            self.api['native_adapter'](self.component, self.session)


    def test_plugin_replacement_invalidates_existing_adapter(self):
        self.adapter._plugin_type = type(self.plugin)
        self.plugin = Owner(_entries={1: self.entry()})
        frame = self.adapter.capture()
        self.assertFalse(frame['available'])
        self.assertEqual(frame['markers'], [])
        self.assertEqual(self.reads, [])

    def test_topography_factory_accepts_only_native_mode_and_published_training_hints(self):
        native_module = 'gui.Scaleform.daapi.view.battle.maps_training.minimap'
        Plugin = type('BotAppearNotificationPlugin', (object,), {'__module__': native_module})
        Component = type('MapsTrainingMinimapComponent', (object,), {'__module__': native_module})
        self.plugin = Plugin()
        entry = self.entry(aoi=False, location=0)
        entry.getOwnVehicleID = lambda: 101
        entry.isGoalForPlayer = lambda: True
        self.plugin._entries = {999: entry}
        component = Component()
        component.getPlugin = lambda name: self.plugin
        component.getBoundingBox = self.component.getBoundingBox
        self.session.arenaVisitor.gui = Owner(guiType=77)
        looked_up, reads = [], []
        self.dp.getVehicleInfo = lambda vehicle_id: looked_up.append(vehicle_id) or Owner(getDisplayedName=lambda: u'Training tank')
        dependencies = {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Driftkings.common': module(xvmInstalled=False),
            'constants': module(ARENA_GUI_TYPE=module(MAPS_TRAINING=77)),
            'Math': module(Matrix=lambda provider: reads.append(provider) or Owner(translation=Owner(x=100, z=200)),
                           Vector3=lambda x, y, z: (x, y, z)),
            'gui.battle_control.battle_constants': module(VEHICLE_LOCATION=module(AOI=1, FAR=2)),
            'gui.battle_control.minimap_utils': module(MINIMAP_SIZE=(210, 210),
                getCellIdFromPosition=lambda *args: 0, getCellName=lambda *args: 'A1')}
        api = source('views/battle/tactical_minimap.py', dependencies)
        adapter = api['native_adapter'](component, self.session)
        frame = adapter.capture()
        self.assertTrue(frame['available'])
        self.assertEqual(frame['context'], 'topography')
        self.assertEqual(frame['markers'], [])
        self.assertEqual(frame['trainingMarkers'][0]['side'], 'training')
        self.assertEqual(frame['trainingMarkers'][0]['state'], 'training')
        self.assertTrue(frame['trainingMarkers'][0]['goal'])
        self.assertEqual(looked_up, [101])  # Target ID 999 is not a vehicle ID.
        entry.isActive = lambda: False
        reads[:] = []
        self.assertEqual(adapter.capture()['trainingMarkers'], [])
        self.assertEqual(reads, [])
        entry.isActive = lambda: True
        self.session.arenaVisitor.gui.guiType = 1
        self.assertFalse(adapter.capture()['available'])
        self.assertEqual(reads, [])
        with self.assertRaises(ValueError):
            api['native_adapter'](component, self.session)
        self.session.arenaVisitor.gui.guiType = 77
        with self.assertRaises(ValueError):
            api['native_adapter'](self.component, self.session)  # Wrong component class.
        dependencies['Driftkings.common'].xvmInstalled = True
        with self.assertRaises(ValueError):
            api['native_adapter'](component, self.session)

    def test_native_factory_uses_verified_constants_and_translation_contract(self):
        NativePlugin = type('NativePlugin', (object,), {
            '__module__': 'gui.Scaleform.daapi.view.battle.shared.minimap.plugins'})
        self.plugin = NativePlugin()
        self.plugin._entries = {1: self.entry()}
        cell_calls = []
        def cell_id(position, bounds, dimensions):
            cell_calls.append((position, bounds, dimensions))
            return 89
        dependencies = {
            'Driftkings.core.tactical_minimap': self.load('core.tactical_minimap'),
            'Driftkings.common': module(xvmInstalled=False),
            'Math': module(Matrix=lambda provider: module(translation=module(x=provider[0], z=provider[1])),
                           Vector3=lambda x, y, z: (x, y, z)),
            'gui.battle_control.battle_constants': module(VEHICLE_LOCATION=module(AOI=1, FAR=2)),
            'gui.battle_control.minimap_utils': module(MINIMAP_SIZE=(210, 210),
                getCellIdFromPosition=cell_id, getCellName=lambda value, dimensions: 'K9' if (value, dimensions) == (89, 10) else None)}
        api = source('views/battle/tactical_minimap.py', dependencies)
        adapter = api['native_adapter'](self.component, self.session)
        frame = adapter.capture()
        self.assertEqual(frame['nativeSize'], (210, 210))
        self.assertEqual(len(frame['markers']), 1)
        self.assertEqual(frame['markers'][0]['cell'], 'K9')
        self.assertEqual(cell_calls, [((100, 0, 200), ((-100, -200), (300, 600)), 10)])
        dependencies['Driftkings.common'].xvmInstalled = True
        with self.assertRaises(ValueError):
            source('views/battle/tactical_minimap.py', dependencies)['native_adapter'](self.component, self.session)
