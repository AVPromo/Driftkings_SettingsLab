# -*- coding: utf-8 -*-
"""Aiming reticles: client globals are changed while enabled and always restored."""
import collections
import json
import os

from support import Event, RuntimeTest, Settings, game_source, module, stub

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
with open(os.path.join(ROOT, 'res', 'configs', 'driftkings', 'default', 'aiming_reticles.json'), 'rb') as stream:
    DEFAULTS = json.loads(stream.read().decode('utf-8-sig'))
MarkerInfo = collections.namedtuple('MarkerInfo', ('size', 'dualAccSize'))
MODES = module(ARCADE='arcade', STRATEGIC='strategic', SNIPER='sniper', ARTY='arty')


class AimingReticlesTests(RuntimeTest):
    def setUp(self):
        super(AimingReticlesTests, self).setUp()
        self.data = dict(DEFAULTS, gunMarkerMinimumSize=18, percentCorrection=50)
        self.synced, self.server = True, []
        self.cache = module(isSynced=lambda: self.synced, onSyncCompleted=Event())
        self.constants = stub('aih_constants', GUN_MARKER_MIN_SIZE=32, CTRL_MODE_NAME=MODES)
        self.factory = stub('gm_factory', _GUN_MARKER_LINKAGES={'native': 'linkage'})
        self.service = Settings(self.data)
        self.service.affects = lambda changes, *keys: any(key in changes for key in keys)
        self.api, self.hooks = game_source('battle/aiming_reticles.py', {
            'driftkings.settings.service': module(settings_service=self.service, affects=self.service.affects),
            'aih_constants': self.constants,
            'gui.Scaleform.daapi.view.battle.shared.crosshair': stub('crosshair', gm_factory=self.factory),
            'helpers': module(dependency=module(instance=lambda interface: self.cache)),
        }, real=('driftkings._constants',))
        self.api['enableServerAiming'] = lambda: self.server.append('enabled')
        self.reticle = self.api['reticle']
        self.reticle.start()
        self.addCleanup(self.reticle.stop)

    def test_start_applies_size_and_correction_then_stop_restores_them(self):
        self.assertEqual(self.constants.GUN_MARKER_MIN_SIZE, 18)
        self.assertAlmostEqual(self.reticle.reticleScaleFactor, 1.355)
        self.reticle.stop()
        self.assertEqual(self.constants.GUN_MARKER_MIN_SIZE, 32)
        self.assertEqual((self.reticle.reticleScaleFactor, self.reticle.showClientAndServerReticle), (1, False))
        self.assertEqual(self.factory._GUN_MARKER_LINKAGES, {'native': 'linkage'})

    def test_disabling_the_module_restores_native_values(self):
        self.data['enabled'] = False
        self.reticle.onModSettingsChanged('aiming_reticles', {'enabled': False})
        self.assertEqual((self.constants.GUN_MARKER_MIN_SIZE, self.reticle.reticleScaleFactor), (32, 1))

    def test_a_change_only_updates_its_own_option(self):
        self.data.update(gunMarkerMinimumSize=24, percentCorrection=0)
        self.reticle.onModSettingsChanged('aiming_reticles', {'gunMarkerMinimumSize': 24})
        self.assertEqual(self.constants.GUN_MARKER_MIN_SIZE, 24)
        self.assertAlmostEqual(self.reticle.reticleScaleFactor, 1.355)

    def test_server_reticle_adds_linkages_and_waits_for_synced_settings(self):
        self.data['showClientAndServerReticleBeta'] = True
        self.reticle.onModSettingsChanged('aiming_reticles', {'showClientAndServerReticleBeta': True})
        self.assertIn('native', self.factory._GUN_MARKER_LINKAGES)
        self.assertGreater(len(self.factory._GUN_MARKER_LINKAGES), 1)
        self.synced = False
        self.reticle.ensureServerAiming()
        self.assertEqual(self.server, [])
        self.cache.onSyncCompleted()
        self.assertEqual(self.server, ['enabled'])
        self.assertEqual(self.cache.onSyncCompleted.handlers, [])
        self.data['showClientAndServerReticleBeta'] = False
        self.reticle.onModSettingsChanged('aiming_reticles', {'showClientAndServerReticleBeta': False})
        self.assertEqual(self.factory._GUN_MARKER_LINKAGES, {'native': 'linkage'})

    def test_marker_size_is_corrected_only_in_the_aiming_modes(self):
        sizes = []
        native = lambda handler, info, support, relax: sizes.append(info.size)
        update = self.hooks.get('AvatarInputHandler', 'updateClientGunMarker')
        update(native, module(ctrlModeName='arcade'), MarkerInfo(271.0, 0.0), None, 0)
        update(native, module(ctrlModeName='arty'), MarkerInfo(271.0, 0.0), None, 0)
        self.assertAlmostEqual(sizes[0], 200.0)
        self.assertEqual(sizes[1], 271.0)
