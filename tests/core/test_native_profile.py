import json
from support import RuntimeTest, Settings, game_source, module


class AccountWN8Tests(RuntimeTest):
    def setUp(self):
        super(AccountWN8Tests, self).setUp()
        self.calculate = self.load('core.profile_ratings').account_wn8
        self.stats = module(getBattlesCount=lambda: 100, getVehicles=lambda: {1: (25, 12, 100), 2: (75, 37, 300)},
                            getAvgDamage=lambda: 1750, getAvgFrags=lambda: 1.75, getAvgEnemiesSpotted=lambda: 1.75,
                            getDroppedCapturePoints=lambda: 175, getWinsEfficiency=lambda: .5)
        self.expected = lambda key: dict(wn8expDamage=1000*key, wn8expFrag=key, wn8expSpot=key,
                                         wn8expDef=key, wn8expWinRate=50)

    def test_weights_expected_values_by_each_vehicles_battles(self):
        self.assertEqual(self.calculate(self.stats, self.expected), 1565)

    def test_incomplete_data_does_not_invent_a_rating(self):
        self.assertIsNone(self.calculate(self.stats, lambda key: None))
        self.stats.getVehicles = lambda: {1: (25, 12, 100)}
        self.assertIsNone(self.calculate(self.stats, self.expected))
        self.stats.getBattlesCount = lambda: 0
        self.assertIsNone(self.calculate(self.stats, self.expected))


class NativeProfileTests(RuntimeTest):
    def test_native_header_fields_vehicle_sorting_and_switches(self):
        settings = {'enabled': True, 'profileRatingColors': True, 'showProfileWN8': True}
        names = ['_BattlesCountField', '_DamageCoefficientField', '_HitsField', '_AvgDmgField',
                 '_WinsEfficiencyField', '_AvgEnemiesSpottedField', '_AvgDestroyedField']
        fields = module(**dict((name, type(name, (object,), {})) for name in names))
        fields.ProfileUtils = module(packLditItemData=lambda text, desc, tip, icon: dict(text=text, description=desc, iconPath=icon))
        api, hooks = game_source('views/hangar/profile_statistics.py', {
            'driftkings.settings.service': Settings(settings).service(),
            'gui.Scaleform.daapi.view.lobby.profile': module(ProfileUtils=fields),
            'gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos': module(ProfileAllStatisticsVO=type('ProfileAllStatisticsVO', (object,), {})),
            'gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique': module(ProfileTechnique=type('ProfileTechnique', (object,), {})),
            'gui.Scaleform.daapi.view.lobby.profile.ProfileStatistics': module(ProfileStatistics=type('ProfileStatistics', (object,), {})),
        }, real=('driftkings.common.utils.colorRatting',))
        api['account_wn8'] = lambda *args: 2200
        api['install']()
        native = [{'text': str(i)} for i in range(6)]
        stats = module(getBattlesCount=lambda: 19, getWinsEfficiency=lambda: .7895, getAvgDamage=lambda: 1357)
        data = [stats, module(getRandomStats=lambda: stats)]
        header = hooks.get('ProfileAllStatisticsVO', '_getHeaderData')
        result = header(lambda *args: native, None, data)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[-1]['description'], 'WN8')
        self.assertIn('2200', result[-1]['text'])
        self.assertEqual(native, [{'text': str(i)} for i in range(6)])
        rows = [{'id': 1, 'shortUserName': 'Tank', 'winsEfficiency': 78.95, 'battlesCount': 19, 'avgExperience': 1022}]
        vehicles = hooks.get('ProfileTechnique', '_getTechniqueListVehicles')
        colored = vehicles(lambda *args: rows, None)
        self.assertIn('<font', colored[0]['shortUserName'])
        self.assertEqual(colored[0]['battlesCount'], 19)
        self.assertEqual(colored[0]['winsEfficiency'], 78.95)
        settings['profileRatingColors'] = False
        self.assertEqual(vehicles(lambda *args: rows, None), rows)
        settings['showProfileWN8'] = False
        self.assertEqual(header(lambda *args: native, None, data), tuple(native))
        settings['profileRatingColors'] = True
        field = hooks.get('_WinsEfficiencyField', '_buildData')
        self.assertIn('<font', field(lambda *args: '78.95%', None, stats, True))
