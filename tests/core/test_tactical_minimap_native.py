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

    def test_hidden_lost_transitional_dead_and_inactive_entries_never_read_matrices(self):
        entries = [self.entry(active=False), self.entry(alive=False), self.entry(aoi=False),
                   self.entry(location=0), self.entry(location=2), self.entry(location=3)]
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
            'gui.battle_control.battle_constants': module(VEHICLE_LOCATION=module(AOI=1)),
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
