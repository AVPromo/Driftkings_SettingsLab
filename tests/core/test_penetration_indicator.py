# -*- coding: utf-8 -*-
"""Penetration indicator: armour along the shot, the result thresholds and crew randomisation."""
from support import RuntimeTest, Settings, game_source, module

RESULT = module(UNDEFINED='undefined', GREAT_PIERCED='great', NOT_PIERCED='not', LITTLE_PIERCED='little')
LOWER_BOUND = 'damageAndPiercingDistributionLowerBound'


def plate(name, armor, dist=0.0, damage=0.0, once=False, kind=1, cos=1.0):
    return module(compName=name, dist=dist, hitAngleCos=cos,
                  matInfo=module(armor=armor, kind=kind, useHitAngle=True, vehicleDamageFactor=damage, collideOnceOnly=once))


def shell(kind='ARMOR_PIERCING', mechanics='LEGACY', loss=0.0, shield=False, caliber=100):
    return module(kind=kind, caliber=caliber,
                  type=module(mechanics=mechanics, piercingPowerLossFactorByDistance=loss, shieldPenetration=shield))


class PenetrationIndicatorTests(RuntimeTest):
    def setUp(self):
        super(PenetrationIndicatorTests, self).setUp()
        self.data = {'enabled': True, 'displayOnAllies': False}
        self.descriptors = {'gunner_armorer': [('other', module(value=9.0)), (LOWER_BOUND, module(value=0.0004))],
                            'loader_ammunitionImprove': [(LOWER_BOUND, module(value=0.0002))]}
        skills = module(getSkill=lambda name: module(uiSettings=module(descrArgs=self.descriptors[name])))
        self.api, self.hooks = game_source('battle/penetration_indicator.py', {
            'Driftkings.settings.service': Settings(self.data).service(),
            'Driftkings.game_constants': module(SHOT_RESULT=RESULT,
                                                SHELL_TYPES=module(HIGH_EXPLOSIVE='HIGH_EXPLOSIVE'),
                                                SHELL_MECHANICS_TYPE=module(MODERN='MODERN')),
            'items.tankmen': module(getSkillsConfig=lambda: skills),
            'gui.shared.gui_items': module(KPI=module(Name=module(DAMAGE_AND_PIERCING_DISTRIBUTION_LOWER_BOUND=LOWER_BOUND))),
        }, real=('Driftkings._constants',))
        self.shot = self.api['_ShotResult']
        # Native helpers of _CrosshairShotResults, reduced to their armour inputs.
        self.shot._computePenetrationArmor = classmethod(lambda cls, shell, cos, mat: mat.armor / cos)
        self.shot._shouldRicochet = classmethod(lambda cls, shell, cos, mat: cos < 0.3)
        self.shot._SHELL_EXTRA_DATA = {'ARMOR_PIERCING': module(hasPenetrationLoss=False),
                                       'HOLLOW_CHARGE': module(hasPenetrationLoss=True)}
        self.addCleanup(setattr, self.shot, 'RANDOMIZATION', self.shot.RANDOMIZATION)

    def test_result_thresholds_follow_the_randomisation(self):
        check = self.shot._checkShotResult
        self.assertEqual(check((70, 100, 0, False, False)), 'great')
        self.assertEqual(check((100, 100, 0, False, False)), 'little')
        self.assertEqual(check((130, 100, 0, False, False)), 'not')
        self.assertEqual(check((10, 100, 0, True, False)), 'undefined')
        self.assertEqual(check((10, 100, 0, False, True)), 'undefined')

    def test_spaced_and_main_armour_add_up_until_the_damaging_plate(self):
        result, data = self.shot._computeArmorDefault(
            [plate('screen', 20), plate('hull', 100, damage=1.0), plate('behind', 500, damage=1.0)], shell(), 200.0, None)
        self.assertEqual(data, (120, 200, 100, False, False))
        self.assertEqual(result, 'great')
        # Only non-damaging plates: no damage, so no prediction.
        result, data = self.shot._computeArmorDefault([plate('screen', 20)], shell(), 200.0, None)
        self.assertEqual((result, data[4]), ('undefined', True))

    def test_ricochet_and_once_only_materials(self):
        result, data = self.shot._computeArmorDefault([plate('hull', 100, damage=1.0, cos=0.2)], shell(), 200.0, None)
        self.assertEqual((result, data[3]), ('undefined', True))
        result, data = self.shot._computeArmorDefault(
            [plate('track', 20, once=True), plate('track', 20, once=True), plate('hull', 50, damage=1.0)], shell(), 200.0, None)
        self.assertEqual(data[0], 70)

    def test_heat_jet_loses_power_after_the_first_plate(self):
        heat = shell(kind='HOLLOW_CHARGE', loss=0.5)
        _, data = self.shot._computeArmorDefault([plate('screen', 20, dist=1.0), plate('hull', 100, dist=1.52, damage=1.0)], heat, 300.0, None)
        # The jet starts 0.02 m behind the screen (armour * 0.001) and travels 0.5 m.
        self.assertEqual(data[:2], (120, 225))

    def test_modern_he_loses_power_on_shields(self):
        he = shell(kind='HIGH_EXPLOSIVE', mechanics='MODERN', shield=True)
        self.assertTrue(self.shot._isModernMechanics(he))
        result, data = self.shot._computeArmorModernHE([plate('screen', 10), plate('hull', 40, damage=1.0)], he, 100.0, None)
        self.assertEqual(data, (50, 70, 100, False, False))
        self.assertEqual(result, 'great')
        # Each shield costs three times its own armour, not the running total.
        _, data = self.shot._computeArmorModernHE([plate('a', 10, kind=1), plate('b', 10, kind=2), plate('hull', 5, damage=1.0)], he, 100.0, None)
        self.assertEqual(data[:2], (25, 40))

    def test_crew_skills_narrow_the_randomisation(self):
        def tankman(*skills):
            return module(canUseSkillsInCurrentVehicle=True, skillsEfficiency=1.0, crewLevelIncrease=(0, None),
                          getPossibleSkills=lambda: set(skills), skillsMap=dict((name, module(level=100)) for name in skills))
        vehicle = module(userName='Tank', crew=[(0, tankman('gunner_armorer')), (1, tankman('loader_ammunitionImprove')), (2, None)])
        randomizer = self.api['Randomizer']
        randomizer.PIERCING_DISTRIBUTION_BOUND.clear()
        randomizer._updateRandomization(vehicle)
        # Gunner: 100 * 0.0004 narrows both bounds; loader: 100 * 0.0002 raises the minimum.
        self.assertEqual(tuple(self.shot.RANDOMIZATION), (0.81, 1.21))
        self.data['enabled'] = False
        randomizer._updateRandomization(vehicle)
        self.assertEqual(tuple(self.shot.RANDOMIZATION), (0.75, 1.25))

    def test_indicator_plugin_is_installed_only_when_enabled(self):
        create = self.hooks.get('plugins', 'createPlugins')
        self.assertIn('shotResultIndicator', create(lambda *args: {}))
        self.data['enabled'] = False
        self.assertNotIn('shotResultIndicator', create(lambda *args: {}))
