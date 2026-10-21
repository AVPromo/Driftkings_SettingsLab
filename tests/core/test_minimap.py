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
