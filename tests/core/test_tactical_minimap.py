# -*- coding: utf-8 -*-
import copy
import io
import json
import os
import shutil
import sys
import tempfile
from support import ROOT, RuntimeTest, module, source


class TacticalMinimapTests(RuntimeTest):
    def setUp(self):
        super(TacticalMinimapTests, self).setUp()
        self.api = self.load('core.tactical_minimap')

    def test_visual_preferences_validate_without_mutating_configuration(self):
        values = {'theme': 'military', 'size': 440, 'followNativeSize': False,
                  'allyColor': '#12ABef', 'showGrid': False}
        original = copy.deepcopy(values)
        result = self.api.preferences(values)
        self.assertEqual(values, original)
        self.assertEqual(result['size'], 440)
        self.assertEqual(result['theme'], 'military')
        self.assertFalse(result['followNativeSize'])
        self.assertFalse(result['showGrid'])
        self.assertEqual(result['fontSize'], 12)
        result['fontSize'] = 20
        self.assertEqual(self.api.preferences()['fontSize'], 12)
        self.api.validate_settings({})  # Existing configurations remain valid.
        for value in ([], False, 'invalid'):
            with self.assertRaises(ValueError):
                self.api.preferences(value)
        for key, values in (
                ('size', [True, '320', 159, 641, 200.5, float('inf')]),
                ('fontSize', [7, 25, 12.5]), ('mapOpacity', [-.1, 1.1, float('nan')]),
                ('iconScale', [.4, 3.1]), ('theme', ['unknown']),
                ('showGrid', [0, 'false']), ('followNativeSize', [1]),
                ('allyColor', ['red', '#12345', '#123456\n'])):
            for value in values:
                with self.assertRaises(ValueError):
                    self.api.preferences({key: value})
        with self.assertRaises(ValueError):
            self.api.validate_settings({'minimapMode': 'unsupported'})
        self.api.validate_settings({'minimapMode': 'driftkings', 'tactical': original})
        self.assertEqual(self.api.selection('driftkings', renderer_ready=True)['effectiveMode'], 'vanilla')

    def test_preferences_survive_split_store_save_and_existing_file_merge(self):
        sys.modules['Driftkings.settings'] = module(__path__=[os.path.join(
            ROOT, 'mod', 'res', 'scripts', 'client', 'Driftkings', 'settings')])
        store_api = self.load('settings.store')
        store = source('settings/minimap_store.py', {
            'Driftkings.settings.store': store_api,
            'Driftkings.settings.loader': module(validate_types=lambda *args: None),
            'Driftkings.core.minimap': self.load('core.minimap')})
        with io.open(os.path.join(ROOT, 'res', 'configs', 'Driftkings', 'default',
                                  'minimap_enhancements.json'), encoding='utf-8') as stream:
            defaults = json.load(stream)
        directory = tempfile.mkdtemp(prefix='dk-minimap-')
        self.addCleanup(shutil.rmtree, directory)
        documents = store['MinimapStore'](directory)
        data = copy.deepcopy(defaults)
        data['minimapMode'] = 'driftkings'
        data['tactical'].update(theme='minimal', followNativeSize=False, size=420)
        documents.save(data)
        self.assertEqual(documents.load(defaults), data)
        general_path = os.path.join(directory, 'minimap.json')
        with io.open(general_path, encoding='utf-8') as stream:
            general = json.load(stream)
        # Simulate an existing installation predating tactical preferences.
        general.pop('minimapMode')
        general.pop('tactical')
        general['zoomFactor'] = 2.1
        with io.open(general_path, 'w', encoding='utf-8') as stream:
            stream.write(type(u'')(json.dumps(general)))
        loaded = documents.load(defaults)
        self.assertEqual(loaded['zoomFactor'], 2.1)
        self.assertEqual(loaded['minimapMode'], 'vanilla')
        self.assertEqual(loaded['tactical'], defaults['tactical'])

    def marker(self, **changes):
        marker = dict(id=1, visible=True, state='visible', side='enemy', vehicleClass='heavyTank',
                      name=u'Test', x=0, z=0, direction=(1, 0))
        marker.update(changes)
        return marker

    def test_default_and_all_unverified_mode_transitions_keep_native_visible(self):
        self.assertEqual(self.api.DEFAULTS['minimapMode'], 'vanilla')
        for mode in ('vanilla', 'driftkings', 'vanilla'):
            for ready in (True, False):
                for conflict in (True, False):
                    state = self.api.selection(mode, conflict, ready)
                    self.assertEqual(state['requestedMode'], mode)
                    self.assertEqual(state['effectiveMode'], 'vanilla')
                    self.assertTrue(state['nativeVisible'])
                    self.assertFalse(state['rendererVisible'])
                    self.assertFalse(state['lostContactAvailable'])
        with self.assertRaises(ValueError):
            self.api.selection('unknown')

    def test_rectangular_offset_maps_and_orientation(self):
        bounds = (-100, -200, 300, 600)
        self.assertEqual(self.api.coordinates(-100, 600, bounds), (0, 0))
        self.assertEqual(self.api.coordinates(300, -200, bounds), (1, 1))
        self.assertEqual(self.api.coordinates(100, 200, bounds), (.5, .5))
        self.assertIsNone(self.api.coordinates(400, 0, bounds))
        for direction, angle in (((0, 1), 0), ((1, 0), 90), ((0, -1), 180), ((-1, 0), 270)):
            self.assertEqual(self.api.heading(*direction), angle)
        self.assertIsNone(self.api.heading(0, 0))

    def test_invalid_geometry_is_rejected(self):
        for bounds in ((0, 0, 0, 1), (1, 1, 0, 0), (0, 0, float('inf'), 1)):
            with self.assertRaises(ValueError):
                self.api.coordinates(0, 0, bounds)
        for value in (True, None, 'invalid', float('nan')):
            with self.assertRaises(ValueError):
                self.api.heading(value, 0)

    def test_invisible_and_lost_entries_are_dropped_before_coordinate_access(self):
        lost = self.marker(state='lost')
        invisible = self.marker(visible=False)
        del lost['x']
        del invisible['z']
        data = self.api.preview_snapshot([lost, invisible], (-1, -1, 1, 1))
        self.assertEqual(data['markers'], [])
        with self.assertRaises(ValueError):
            self.api.preview_snapshot([], (-1, -1, 1, 1), source='battle')

    def test_snapshot_has_no_position_retention_between_frames(self):
        marker = self.marker()
        original = copy.deepcopy(marker)
        first = self.api.preview_snapshot([marker], (-1, -1, 1, 1))
        self.assertEqual(first['markers'][0]['heading'], 90)
        self.assertEqual(marker, original)
        self.assertEqual(self.api.preview_snapshot([], (-1, -1, 1, 1))['markers'], [])
        destroyed = self.api.preview_snapshot([self.marker(state='destroyed')], (-1, -1, 1, 1))
        self.assertNotIn('heading', destroyed['markers'][0])

    def test_marker_semantics_are_bounded_and_duplicate_ids_fail(self):
        for changes in (dict(side='hidden'), dict(vehicleClass='unknown'), dict(id=True)):
            with self.assertRaises(ValueError):
                self.api.preview_snapshot([self.marker(**changes)], (-1, -1, 1, 1))
        with self.assertRaises(ValueError):
            self.api.preview_snapshot([self.marker(), self.marker()], (-1, -1, 1, 1))


    def test_click_conversion_and_inverse_match_native_rectangular_geometry(self):
        bounds = (-100, -200, 300, 600)
        for world in ((-100, -200), (-100, 600), (300, -200), (300, 600), (100, 200)):
            normalized = self.api.coordinates(world[0], world[1], bounds)
            self.assertEqual(self.api.world_point(normalized[0], normalized[1], bounds), world)
        self.assertEqual(self.api.native_click_point(0.5, 0.5, (210, 210)), (105, 105))
        self.assertEqual(self.api.native_click_point(1, 0, (210, 210)), (210, 0))
        with self.assertRaises(ValueError):
            self.api.native_click_point(1.1, 0, (210, 210))
        with self.assertRaises(ValueError):
            self.api.world_point(0, float('nan'), bounds)
