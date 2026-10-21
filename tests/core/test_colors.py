# -*- coding: utf-8 -*-
from support import RuntimeTest


class ColorTests(RuntimeTest):
    def setUp(self):
        super(ColorTests, self).setUp()
        self.colors = self.load('common.utils.colorRatting')

    def test_extracted_tables_preserve_legacy_exports_and_shared_identity(self):
        data = self.load('common.utils.color_rating_data')
        self.assertEqual(self.colors.__all__, ('color_tables', 'getRatingColors', 'getColor', 'getStatisticColor',
                                               'getRatingPaletteColor', 'getComparisonColor', 'getMoeDamageColor'))
        for name in ('MOE_LEVELS', 'color_tables'):
            self.assertIs(getattr(self.colors, name), getattr(data, name))

    def test_all_numeric_scales_at_below_and_above_every_boundary(self):
        api = self.colors
        checked = 0
        for table in api.color_tables:
            for metric, bands in table['colors'].items():
                if not isinstance(bands, (list, tuple)) or metric in ('diff', 'mog'):
                    continue
                for index, band in enumerate(bands):
                    limit = band['value']
                    # Source scales use exclusive upper bounds, not <=.
                    lower = api.formatColor(band['color'])
                    upper = api.formatColor(bands[min(index + 1, len(bands) - 1)]['color'])
                    self.assertEqual(api.getColor(table['colors'], metric, limit - 0.00001), lower)
                    self.assertEqual(api.getColor(table['colors'], metric, limit), upper)
                    self.assertEqual(api.getColor(table['colors'], metric, limit + 0.00001), upper)
                    checked += 1
                self.assertEqual(api.getColor(table['colors'], metric, -1e40), api.formatColor(bands[0]['color']))
                self.assertEqual(api.getColor(table['colors'], metric, 1e40), api.formatColor(bands[-1]['color']))
        self.assertGreater(checked, 100)

    def test_moe_inclusive_lower_bounds_and_outside_range(self):
        api = self.colors
        for index in range(len(api.color_tables)):
            bands = api.getRatingColors(index)['mog']
            for position, band in enumerate(bands):
                self.assertEqual(api.getStatisticColor('mog', band['value'], index), api.formatColor(band['color']))
                self.assertEqual(api.getStatisticColor('mog', band['value'] - 0.001, index),
                                 api.formatColor(bands[max(0, position - 1)]['color']))
            self.assertEqual(api.getStatisticColor('mog', -10, index), '#FFFFFF')
            self.assertEqual(api.getStatisticColor('mog', 101, index), api.formatColor(bands[-1]['color']))

    def test_invalid_palette_and_metric_fallbacks(self):
        api = self.colors
        first = api.getRatingColors(0)
        for value in (-1, 3, 100, None, 'unknown', float('nan'), float('inf')):
            self.assertIs(api.getRatingColors(value), first)
        self.assertIs(api.getRatingColors('1'), api.getRatingColors(1))
        for index in range(3):
            data = api.getRatingColors(index)
            self.assertIsNone(api.getColor(data, 'missing', 100))
            for value in (None, 'invalid', float('nan'), float('inf'), -float('inf')):
                self.assertIsNone(api.getColor(data, 'wn8', value))
                self.assertEqual(api.getStatisticColor('wn8', value, index), api.getRatingPaletteColor('nocolor', index))
            self.assertEqual(api.getStatisticColor('missing', 100, index), api.getRatingPaletteColor('nocolor', index))

    def test_aliases_and_battle_units(self):
        api = self.colors
        for index in range(3):
            data = api.getRatingColors(index)
            for alias, metric in (('xwn8', 'x'), ('xeff', 'x'), ('marks', 'mog'), ('winRate', 'winrate'),
                                  ('avgDamage', 'tdb'), ('hitRate', 'hitsRatio')):
                for value in (0, 50, 100, 1000):
                    self.assertEqual(api.getColor(data, alias, value), api.getColor(data, metric, value))
            self.assertEqual(api.getColor(data, 'battles', 10000), api.getColor(data, 'kb', 10))
            self.assertEqual(api.getColor(data, 'unused', kwargs=50), api.getColor(data, 'x', 50))

    def test_comparisons_negative_zero_positive_and_invalid(self):
        api = self.colors
        for index in range(3):
            palette = api.getRatingColors(index)['colorRating']
            for value, name in ((9, 'very_bad'), (10, 'normal'), (11, 'good')):
                self.assertEqual(api.getComparisonColor(value, 10, index), api.formatColor(palette[name]))
            for value in (None, 'bad', float('nan'), float('inf')):
                self.assertEqual(api.getComparisonColor(value, 10, index), api.getRatingPaletteColor('nocolor', index))

    def test_moe_damage_target_boundaries(self):
        api = self.colors
        targets = (100, 200, 300, 400, 500, 600, 700)
        for index in range(3):
            for position, target in enumerate(targets):
                for value in (target - 0.01, target):
                    self.assertEqual(api.getMoeDamageColor(value, targets, index),
                                     api.getStatisticColor('mog', api.MOE_LEVELS[position + 1], index))
                self.assertEqual(api.getMoeDamageColor(target + 0.01, targets, index),
                                 api.getStatisticColor('mog', api.MOE_LEVELS[min(position + 2, 7)], index))
            for value in (None, 'bad', float('nan'), float('inf')):
                self.assertEqual(api.getMoeDamageColor(value, targets, index), api.getRatingPaletteColor('nocolor', index))
            self.assertEqual(api.getMoeDamageColor(1, (), index), api.getRatingPaletteColor('nocolor', index))
