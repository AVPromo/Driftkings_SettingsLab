# -*- coding: utf-8 -*-
"""Statistics boundaries and cache recovery without the game or network."""
import json
import os
import shutil
import tempfile
from support import RuntimeTest, module, source


class StatsTests(RuntimeTest):
    def setUp(self):
        super(StatsTests, self).setUp()
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory)
        self.response = b'{"xwn8": [100, 200]}'
        self.failure = None
        self.network = module(urlopen=self.download)
        store = source('settings/store.py', {})
        filesystem = source('common/utils/filesystem.py', {'Driftkings.settings.store': module(**store)})
        self.api = source('stats/vehinfo.py', {
            'urllib2': self.network, 'ResMgr': module(), 'nations': module(NAMES=[]),
            'items': module(vehicles=module()),
            'Driftkings.core.callbacks': module(callback=lambda *args: None),
            'Driftkings.common.utils.filesystem': module(**filesystem),
            'Driftkings.core.cache': module(cache_directory=lambda name: self.directory),
        })
        self.api['open'] = lambda *args, **kwargs: open(*args, **kwargs)
        self.scale = self.api['scaleValuesInstance']
        self.api['LOG'] = module(exception=lambda *args: None, warning=lambda *args: None)

    def download(self, url, timeout):
        if self.failure:
            raise self.failure
        return module(read=lambda: self.response, close=lambda: None)

    def test_scale_endpoints_and_invalid_values(self):
        self.scale.xvmScale_data = {'xwn8': [100, 200]}
        for value, expected in ((0, 0), (99, 0), (100, 1), (199, 1), (200, 100)):
            self.assertEqual(self.scale.calculateXvmScale('wn8', value), expected)
        self.assertEqual(self.scale.calculateXvmScale('missing', 100), -1)
        for value in (None, float('nan'), float('inf')):
            self.assertEqual(self.scale.calculateXvmScale('wn8', value), -1)
        for value, expected in ((None, None), (0, 0.0), (1, '1'), (99, '99'), (100, '100'), (101, '100')):
            self.assertEqual(self.scale.XvmScaleToSup(value), expected)

    def test_invalid_download_preserves_existing_cache(self):
        path = os.path.join(self.directory, 'xvmScales.json')
        original = b'{"xwn8": [5, 10]}'
        with open(path, 'wb') as stream:
            stream.write(original)
        for response in (b'<html>unavailable</html>', b'[]', b'{}'):
            self.response = response
            self.assertFalse(self.scale.loadJsonData('test', path))
            with open(path, 'rb') as stream:
                self.assertEqual(stream.read(), original)
        self.failure = IOError('offline')
        self.scale._loadXvmScaleData()
        self.assertEqual(self.scale.xvmScale_data, {'xwn8': [5, 10]})

    def test_valid_download_and_publish_failure(self):
        path = os.path.join(self.directory, 'xvmScales.json')
        self.assertTrue(self.scale.loadJsonData('test', path))
        with open(path, 'rb') as stream:
            self.assertEqual(json.load(stream), {'xwn8': [100, 200]})
        def fail(path, data):
            raise IOError('disk full')
        self.api['atomicWrite'] = fail
        self.assertFalse(self.scale.loadJsonData('test', path))
        with open(path, 'rb') as stream:
            self.assertEqual(json.load(stream), {'xwn8': [100, 200]})

    def test_missing_and_degenerate_vehicle_ratings(self):
        self.assertEqual(self.scale.calculateXTE(1, 10, 1), -1)
        for data in ({}, {'ad': 0, 'td': 10, 'af': 0, 'tf': 1, 'x': [10]},
                     {'ad': 10, 'td': 10, 'af': 1, 'tf': 2, 'x': [10]}):
            self.scale.xte_data = {'1': data}
            self.assertEqual(self.scale.calculateXTE(1, 10, 1), -1)
        self.scale.xte_data = {'1': {'ad': 100, 'td': 200, 'af': 1, 'tf': 2, 'x': [500, 1000, 1500]}}
        self.assertEqual(self.scale.calculateXTE(1, 100, 1), 2)
        self.scale.xtdb_data = {'1': {'x': [100, 200]}}
        self.assertEqual(self.scale.calculateXTDB(1, 100), 1)
        self.assertEqual(self.scale.calculateXTDB(1, 200), 100)
        self.scale.xtdb_data = {'1': {'x': [200, 100]}}
        self.assertEqual(self.scale.calculateXTDB(1, 150), -1)

    def test_player_aliases_none_ratings_and_missing_hp(self):
        self.scale.vehicleInfoData[1] = {'level': 6}
        api = source('stats/xvm_stats.py', {'Driftkings.stats.vehinfo': module(**self.api)})
        stats = api['xvm_stat']
        value = {'_id': 5, 'b': 10, 'w': 5, 'wn8': None, 'v': None, 'ver': 1,
                 'vehicles': {'bad': {}, '1': {'b': 10, 'w': 5, 'dmg': 1000}}}
        stats._fix_common(value)
        stats._fix_common2(value, 'Player')
        self.assertEqual(value['player_id'], 5)
        self.assertEqual(value['winrate'], 50.0)
        self.assertEqual(value['vehicles']['1']['db'], 100.0)
        self.assertNotIn('dv', value['vehicles']['1'])
        self.assertIsNone(value['wn8'])
        self.assertNotIn('_id', value)
