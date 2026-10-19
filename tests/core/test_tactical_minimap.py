# -*- coding: utf-8 -*-
import copy
from support import RuntimeTest


class TacticalMinimapTests(RuntimeTest):
    def setUp(self):
        super(TacticalMinimapTests, self).setUp()
        self.api = self.load('core.tactical_minimap')

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
