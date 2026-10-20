# -*- coding: utf-8 -*-
"""Retired settings must not survive load/apply or erase personal preferences."""
import copy
import json
import os

from support import ROOT, RuntimeTest, module, source


class RetiredDefaultsTests(RuntimeTest):
    def definition(self, relative, name, section):
        schema = source('settings/controls_schema.py', {})
        api = source(relative, {
            'Driftkings._constants': self.load('_constants'),
            'Driftkings.settings.controls_schema': module(control=schema['control'], slider=schema['slider']),
            'Driftkings.settings.definitions.base': module(SectionDefinition=object),
        })
        return api[name]()

    def defaults(self, name):
        with open(os.path.join(ROOT, 'res/configs/Driftkings/default', name + '.json'), 'rb') as stream:
            return json.load(stream)

    def test_clock_load_and_apply_preserve_custom_format_position_and_unrelated_settings(self):
        definition = self.definition('settings/definitions/lobby/hangar_preferences.py',
                                     'HangarPreferencesSettings', 'HANGAR_PREFERENCES')
        active = {'enabled': False, 'clock': True, 'clockBackground': True, 'clockScale': 125,
                  'clockX': -456, 'clockY': 123, 'customClockText': u'<font>%I:%M %p — %A</font>',
                  'accountManager': {'enabled': True}, 'personalOption': {'keep': [1, 2]}}
        legacy = dict(active, clockStyle=4, clockSeconds=True, clock24Hour=False,
                      customClockFormat=False, text='old', panel={'x': 999})
        for normalize in (definition.normalize_loaded, lambda values: definition.normalize_changes(values, {})):
            values = normalize(copy.deepcopy(legacy))
            self.assertEqual(values, active)
            self.assertEqual(normalize(copy.deepcopy(values)), active)

    def test_native_target_box_preserves_enabled_and_removes_acquisition_options(self):
        definition = self.definition('settings/definitions/battle/autoaim_target_indicator.py',
                                     'AutoaimTargetIndicatorSettings', 'AUTOAIM_TARGET_INDICATOR')
        for enabled in (False, True):
            active = {'enabled': enabled, 'personalOption': 'keep'}
            legacy = dict(active, angle=1.3, catchHiddenTarget=True, disableArtyMode=True)
            self.assertEqual(definition.normalize_loaded(copy.deepcopy(legacy)), active)
            self.assertEqual(definition.normalize_changes(copy.deepcopy(legacy), {}), active)
            self.assertEqual(definition.getControlColumns()[0][0]['varName'], 'color')

    def test_canonical_defaults_contain_current_options_only(self):
        hangar = self.defaults('hangar_preferences')
        self.assertFalse(set(hangar).intersection(('clockStyle', 'clockSeconds', 'clock24Hour', 'customClockFormat')))
        self.assertTrue(all(key in hangar for key in
                            ('clock', 'clockBackground', 'clockX', 'clockY', 'clockScale', 'customClockText', 'accountManager')))
        self.assertEqual(self.defaults('autoaim_target_indicator'), {'enabled': True, 'color': '#F98600'})
