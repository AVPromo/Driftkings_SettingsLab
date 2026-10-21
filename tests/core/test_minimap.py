# -*- coding: utf-8 -*-
"""Minimap policy: shell range lookup and validation of lines in metres, hull line and shell circle."""
import json
import os

from support import RuntimeTest, module

ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'res', 'configs', 'Driftkings', 'default', 'minimap_enhancements')


def defaults():
    data = {}
    for name in ('minimap.json', 'minimap_labels.json', 'minimap_circles.json', 'minimap_lines.json'):
        with open(os.path.join(ROOT, name), 'rb') as stream:
            data.update(json.loads(stream.read().decode('utf-8-sig')))
    return data


class MinimapPolicyTests(RuntimeTest):
    def setUp(self):
        super(MinimapPolicyTests, self).setUp()
        self.policy = self.load('core.minimap')

    def shot(self, cd, distance):
        return module(shell=module(compactDescr=cd), maxDistance=distance)

    def test_shell_range_follows_the_selected_shell(self):
        descriptor = module(gun=module(shots=[self.shot(1, 720.0), self.shot(2, 1250.0)]), shot=self.shot(1, 720.0))
        self.assertEqual(self.policy.shell_range(descriptor, 2), 1250.0)
        self.assertEqual(self.policy.shell_range(descriptor, 1), 720.0)
        # Unknown or missing shell: the active shot of the descriptor.
        self.assertEqual(self.policy.shell_range(descriptor, 99), 720.0)
        self.assertIsNone(self.policy.shell_range(None, 1))

    def test_defaults_enable_hull_line_marks_and_shell_circle(self):
        data = defaults()
        self.policy.validate(data)
        self.assertTrue(data['lines']['hull'])
        self.assertEqual(data['lines']['marks'], 100)
        self.assertEqual(data['circles']['shell']['mode'], 'on')

    def test_invalid_new_options_are_rejected(self):
        for section, key, value in (('lines', 'hull', 'yes'), ('lines', 'marks', 600), ('lines', 'hullColor', 'green')):
            data = defaults()
            data[section][key] = value
            self.assertRaises(ValueError, self.policy.validate, data)
        data = defaults()
        data['circles']['shell']['mode'] = 'client'
        self.assertRaises(ValueError, self.policy.validate, data)
        data = defaults()
        del data['circles']['shell']
        self.assertRaises(ValueError, self.policy.validate, data)

    def test_groups_follow_native_gui_properties(self):
        group = self.policy.vehicle_group
        self.assertEqual([group('ally', False), group('teamKiller', False), group('squadman', False), group('enemy', True)],
                         ['ally', 'teamKiller', 'squad', 'enemy'])
        # A squadmate is never an enemy; a missing label falls back to the side.
        self.assertEqual((group(None, True), group('', False)), ('enemy', 'ally'))

    def test_team_colors_come_from_the_shared_scheme(self):
        system = self.load('common.utils.color_rating_data').system_colors
        color = self.policy.team_color
        self.assertEqual(color('enemy', 'dead'), system['enemy_dead'])
        self.assertEqual(color('squad', 'alive'), system['squadman_alive'])
        self.assertEqual(color('teamKiller', 'dead'), system['teamKiller_dead'])
        # Lost vehicles keep the alive colour; the icon is desaturated instead.
        self.assertEqual(color('ally', 'lost'), system['ally_alive'])

    def test_palettes_share_one_system_table(self):
        data = self.load('common.utils.color_rating_data')
        self.assertTrue(data.noob_meter_colors['system'] is data.xvm_colors['system'] is data.wot_labs_colors['system'])

    def test_dead_and_lost_options_are_validated(self):
        for section, key, value in (('icons', 'deadAlpha', 150), ('lostMarker', 'desaturate', -1),
                                    ('labels', 'teamColors', 1), ('labels', 'teamKillerColor', 'blue')):
            data = defaults()
            data[section][key] = value
            self.assertRaises(ValueError, self.policy.validate, data)
