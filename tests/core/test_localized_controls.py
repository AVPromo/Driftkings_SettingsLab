# -*- coding: utf-8 -*-
"""Every live settings declaration resolves against every bundled language."""
import copy
import os
import sys

from support import CLIENT, ROOT, RuntimeTest, module


class LocalizedControlTests(RuntimeTest):
    def setUp(self):
        super(LocalizedControlTests, self).setUp()
        for name, relative in (('driftkings.settings', 'settings'),
                               ('driftkings.settings.panel', 'settings/panel'),
                               ('driftkings.settings.definitions', 'settings/definitions')):
            sys.modules[name] = module(__path__=[os.path.join(CLIENT, relative)])
        self.defaults = self.load('settings.default_values').DEFAULTS
        self.schema = self.load('settings.controls_schema')
        self.parser = self.load('core.locale_catalog').parse_catalog
        self.documents = {}
        for code, _ in self.load('locale_support').LANGUAGES:
            with open(os.path.join(ROOT, 'mod/res/mods/driftkings/text', code + '.yml'), 'rb') as stream:
                self.documents[code] = self.parser(stream.read())['TEXT']
        test = self
        class Base(object):
            NAME = None
            COLUMNS = ((), ())
            def __init__(self):
                self.data = copy.deepcopy(test.defaults.get(self.NAME, {}))
                self.i18n = dict(test.text.get('common', {}))
                self.i18n.update(test.text.get(self.NAME, {}))
            def getControlColumns(self):
                return self.COLUMNS
        self.Base = Base
        sys.modules['driftkings.settings.definitions.base'] = module(SectionDefinition=Base)
        sys.modules['driftkings.settings.service'] = module(
            settings_service=module(getComponentDict=lambda config: config.data))
        sys.modules['driftkings.settings.panel.media'] = module(SIXTH_SENSE_EVENTS=('sixthSense',))
        class Names(object):
            def __getattr__(self, key):
                return key
        for name, stub in (
                ('ResMgr', module(openSection=lambda path: module(keys=lambda: ['0.png', '1.png']))),
                ('gui', module(__path__=[])),
                ('gui.Scaleform', module(__path__=[])),
                ('gui.Scaleform.locale', module(__path__=[])),
                ('gui.Scaleform.locale.SETTINGS', module(SETTINGS=Names())),
                ('helpers', module(i18n=module(makeString=lambda text: text)))):
            previous = sys.modules.get(name)
            sys.modules[name] = stub
            self.addCleanup(self.restore_external, name, previous)
        self.definitions = []
        for area in ('battle', 'lobby', 'components'):
            for filename in sorted(os.listdir(os.path.join(CLIENT, 'settings/definitions', area))):
                if not filename.endswith('.py') or filename == '__init__.py':
                    continue
                api = self.load('settings.definitions.' + area + '.' + filename[:-3])
                # Python 2 compatibility names used by two existing definitions.
                api.xrange = range
                api.basestring = type('')
                cls = next(value for value in vars(api).values()
                           if isinstance(value, type) and value is not Base and issubclass(value, Base))
                self.definitions.append(cls)

    @staticmethod
    def restore_external(name, previous):
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous

    def test_all_current_controls_have_resolvable_localized_labels(self):
        for code, text in self.documents.items():
            self.text = text
            for definition in self.definitions:
                config = definition()
                for column in config.getControlColumns():
                    for declaration in column:
                        resolved = self.schema.resolve(declaration, config.i18n, config.data)
                        if declaration.get('type') != 'Empty':
                            self.assertTrue(resolved.get('text'), (code, config.NAME, declaration))

    def test_distance_choices_and_team_tabs_use_each_selected_language(self):
        for code, text in self.documents.items():
            self.text = text
            for definition in self.definitions:
                if definition.NAME == 'target_distance':
                    config = definition()
                    for position, item in enumerate(config.getControlColumns()[0]):
                        for index, option in enumerate(item.get('options', [])):
                            internal = definition.COLUMNS[0][position]['options'][index]['label']
                            self.assertEqual(option['label'], config.i18n['UI_setting_' + item['varName'] + '_' + internal])
                elif definition.NAME == 'team_panels':
                    config = definition()
                    tabs = set(item.get('tab') for column in config.getControlColumns() for item in column)
                    for key in ('generalTab', 'loadingTab', 'templatesTab'):
                        self.assertIn(config.i18n['UI_panel_' + key], tabs, code)
