# -*- coding: utf-8 -*-
"""Small battle modules: server turret sync, distance marker lifecycle and view entry points."""
from support import RuntimeTest, Settings, game_source, module


class ServerTurretSyncTests(RuntimeTest):
    def setUp(self):
        super(ServerTurretSyncTests, self).setUp()
        self.data = {'enabled': True, 'serverTurret': True, 'activateMessage': True}
        self.scheduled = []
        self.api, self.hooks = game_source('battle/server_turret_sync.py', {
            'Driftkings.settings.service': Settings(self.data).service(),
            'Driftkings.core.callbacks': module(callback=lambda delay, function: self.scheduled.append(delay)),
        }, real=('Driftkings._constants',))
        self.wrapper = self.hooks.get('VehicleGunRotator', 'setShotPosition')

    def rotate(self):
        calls = []
        rotator = module(_avatar=module(vehicle=module(getServerGunAngles=lambda: (0.4, -0.1))),
                         _VehicleGunRotator__turretYaw=0.0, _VehicleGunRotator__gunPitch=0.0)
        self.wrapper(lambda *args: calls.append(args), rotator, 1, 'pos', 'vec', 0.01)
        return rotator, calls[0]

    def test_shot_position_uses_the_server_gun_angles(self):
        rotator, call = self.rotate()
        self.assertEqual((rotator._VehicleGunRotator__turretYaw, rotator._VehicleGunRotator__gunPitch), (0.4, -0.1))
        self.assertIs(call[-1], True)

    def test_disabled_option_or_module_keeps_the_client_angles(self):
        for key in ('serverTurret', 'enabled'):
            self.data.update(enabled=True, serverTurret=True)
            self.data[key] = False
            rotator, call = self.rotate()
            self.assertEqual(rotator._VehicleGunRotator__turretYaw, 0.0)
            self.assertIs(call[-1], False)

    def test_activation_message_is_scheduled_at_battle_start(self):
        start = self.hooks.events['Driftkings.common.utils.events.PlayerAvatar.startGUI.after'][0]
        start()
        self.data['activateMessage'] = False
        start()
        self.assertEqual(self.scheduled, [5.0])


class TargetDistanceTests(RuntimeTest):
    def setUp(self):
        super(TargetDistanceTests, self).setUp()
        self.data = {'enabled': True}
        self.created, self.moves = [], []
        test = self

        class Controller(object):
            def __init__(self, clazz):
                self.closed = False
                test.created.append(self)

            def close(self):
                self.closed = True

            @staticmethod
            def onMouseEvent(dx, dy):
                test.moves.append((dx, dy))

        self.api, self.hooks = game_source('battle/target_distance.py', {
            'Driftkings.settings.service': Settings(self.data).service(),
            'Driftkings.views.battle.target_distance': module(DistanceMarkerController=Controller,
                                                              DistanceMarkerView=object, ALIAS='alias'),
        }, real=('Driftkings._constants',))

    def test_marker_lives_between_plugin_start_and_stop(self):
        plugin = module(_clazz='markers')
        mouse = self.hooks.get('AvatarInputHandler', 'handleMouseEvent')
        mouse(lambda handler, event: None, 'handler', module(dx=1, dy=2))
        self.hooks.get('VehicleMarkerPlugin', 'start')(lambda plugin: None, plugin)
        mouse(lambda handler, event: None, 'handler', module(dx=3, dy=4))
        self.hooks.get('VehicleMarkerPlugin', 'start')(lambda plugin: None, plugin)
        self.assertEqual((len(self.created), self.moves), (1, [(3, 4)]))
        self.hooks.get('VehicleMarkerPlugin', 'stop')(lambda plugin: None, plugin)
        self.assertTrue(self.created[0].closed)
        self.assertIsNone(self.api['g_distanceMarker'])

    def test_disabled_module_creates_no_marker(self):
        self.data['enabled'] = False
        self.hooks.get('VehicleMarkerPlugin', 'start')(lambda plugin: None, module(_clazz='markers'))
        self.assertEqual(self.created, [])


class EntryPointTests(RuntimeTest):
    def test_view_modules_register_their_battle_view(self):
        for name, view in (('aiming_countdown', 'DispersionTimer'), ('shell_flight_time', None), ('vehicle_health', None)):
            api, _ = game_source('battle/%s.py' % name, real=('Driftkings._constants',))
            views = api['getBattleViews']()
            self.assertEqual(len(views), 1, name)
            alias, view_class, config = views[0]
            self.assertIs(config, api['config'], name)
            self.assertTrue(alias, name)


class BattlePerformanceWn8Tests(RuntimeTest):
    def test_expected_values_below_one_are_not_rounded_up(self):
        expected = {'level': 8, 'wn8expDamage': 1500.0, 'wn8expSpot': 1.2, 'wn8expFrag': 0.9, 'wn8expDef': 0.6, 'wn8expWinRate': 52.0}
        api, _ = game_source('components/battle_performance.py', {
            'Driftkings.stats.vehinfo': module(getVehicleInfoData=lambda cd: expected, calculateXvmScale=lambda name, value: 0,
                                               calculateXTE=lambda cd, damage, frags: 0),
            'Driftkings.settings.service': Settings({'enabled': True}).service(),
        }, real=('Driftkings._constants',))
        calculator = api['EfficiencyCalculator']()
        calculator.registerVInfoData(1)
        ratios = calculator.calculate_ratios(1500, 1.2, 0.9, 0.6, False)
        self.assertEqual([round(value, 6) for value in ratios[:4]], [1.0, 1.0, 1.0, 1.0])
        expected['wn8expDef'] = 0
        calculator.registerVInfoData(1)
        self.assertEqual(calculator.calculate_ratios(1500, 1, 1, 1, True)[3], 0.0)
