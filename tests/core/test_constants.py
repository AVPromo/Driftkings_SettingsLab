# -*- coding: utf-8 -*-
"""Engine-free constants and tuple contracts used by existing callers."""
import unittest
from support import RuntimeTest, source


class ConstantsTests(RuntimeTest):
    def test_constants_import_without_game_and_share_mark_limits(self):
        constants = self.load('_constants')
        marks = self.load('core.marks_calculator')
        colors = self.load('common.utils.color_rating_data')
        self.assertIs(marks.MARK_LEVELS, constants.MARK_LEVELS)
        self.assertIs(colors.MOE_LEVELS, constants.MARK_LEVELS)
        self.assertIs(marks.THRESHOLDS, constants.MARK_THRESHOLDS)
        self.assertEqual(constants.THIRD_PERSON_ZOOM.MODES, ('arcade', 'postmortem', 'strategic', 'arty'))

    def test_named_records_preserve_tuple_shape_and_are_immutable(self):
        constants = self.load('_constants')
        bounds = constants.ScreenBounds(1, 2, 3, 4)
        self.assertEqual(bounds, (1, 2, 3, 4))
        self.assertEqual(bounds.width, 3)
        with self.assertRaises(AttributeError):
            bounds.width = 10
        marks = self.load('core.marks_calculator')
        stats = marks.statistics(65, 100)
        self.assertIsInstance(stats, constants.MarksStatistics)
        self.assertEqual(len(stats), 9)
        self.assertEqual(stats.next_percent, stats[0])
        self.assertEqual(stats.damage95, stats[7])
        curve = marks.battle_curve([60, 90, 65, 100], 65, 100)
        self.assertIsInstance(curve, constants.BattleCurve)
        self.assertEqual(len(curve), 6)
        self.assertEqual(curve.target_damage, curve[3])
        self.assertEqual(curve.statistics, stats)

    def test_service_spec_preserves_defaults_and_normalizes_dependencies(self):
        api = source('core/__init__.py', {})
        spec = api['ServiceSpec']('test', object, ['common'])
        self.assertEqual(spec.requires, ('common',))
        self.assertEqual(spec.phase, 'foundation')
        self.assertEqual(api['ServiceSpec']('test', object).requires, ())
        with self.assertRaises(AttributeError):
            spec.phase = 'other'


if __name__ == '__main__':
    unittest.main()
