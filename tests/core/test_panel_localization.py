# -*- coding: utf-8 -*-
"""Run the actual roster pipeline with engine boundaries stubbed."""
import ast
import copy
import os

from support import CLIENT, RuntimeTest, module, source


def literal_assignment(relative, name):
    with open(os.path.join(CLIENT, *relative.split('/')), 'rb') as stream:
        tree = ast.parse(stream.read())
    return next(ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name
                                                       for target in node.targets))


class PanelLocalizationTests(RuntimeTest):
    def setUp(self):
        super(PanelLocalizationTests, self).setUp()
        with open(os.path.join(CLIENT, '_constants.py'), 'rb') as stream:
            tree = ast.parse(stream.read())
        panel = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'TEAM_PANELS')
        keys = dict((node.targets[0].id, ast.literal_eval(node.value)) for node in panel.body
                    if isinstance(node, ast.Assign))
        constants = module(TEAM_PANELS=module(**keys), GLOBAL=module(ENABLED='enabled'),
                           BATTLE_ALIASES=module(PLAYERS_PANEL='testRoster'))
        profiles = ('none', 'short', 'medium', 'medium2', 'large')
        settings_data = module(PROFILES=profiles, defaults=lambda name: {}, profile_for_mode=lambda name: name)
        store = source('settings/team_panel_store.py', {
            'Driftkings.core.keycodes': module(valid_key_code=lambda key: True),
            'Driftkings.settings.panel_validation': module(macro_issues=lambda text: []),
            'Driftkings.settings.settings_data': settings_data,
            'Driftkings.settings.store': module(merge=None, JsonDocuments=object, read_object=None),
        })
        self.roster = source('core/panel_model.py', {
            'Driftkings._constants': constants,
            'Driftkings.settings.team_panel_store': module(resolve_fields=store['resolve_fields']),
        })['Roster']
        self.data = copy.deepcopy(literal_assignment('settings/default_values.py', 'DEFAULTS')['team_panels'])
        screen = {'enabled': True, 'showUnavailable': True,
                  'format': '{{region}} / {{l10n:Destroyed}}',
                  'extraFieldsLeft': [{'format': '{{l10n:Destroyed}}'}],
                  'extraFieldsRight': []}
        self.data['profiles'] = {'large': screen}
        self.data['loading'] = copy.deepcopy(screen)
        self.data['tab'] = copy.deepcopy(screen)
        self.config = module(i18n={'UI_panel_destroyed': 'Destroyed'})
        self.player = module(playerVehicleID=1, team=1,
                             arena=module(guiType=1, statistics={}, vehicles={1: {
                                 'name': 'Example', 'team': 1, 'accountDBID': 1500000000,
                                 'isAlive': False}}))
        self.api = source('views/battle/player_ratings.py', {
            'Driftkings._constants': constants,
            'Driftkings.settings.service': module(settings_service=module(getComponentDict=lambda config: self.data),
                                                 SettingsChanges=lambda *args: (), changed_paths=lambda *args: (),
                                                 affects=lambda *args: True),
            'BigWorld': module(player=lambda: self.player),
            'realm': module(CURRENT_REALM='EU'),
            'Driftkings.meta.battle.players_panel': module(PlayersPanelMeta=object),
            'gui.Scaleform.daapi.view.battle.classic.players_panel': module(PlayersPanel=object),
            'gui.Scaleform.daapi.view.meta.BattleStatisticDataControllerMeta': module(BattleStatisticDataControllerMeta=object),
            'gui.shared': module(g_eventBus=None, events=None, EVENT_BUS_SCOPE=None),
            'Driftkings.core.hooks': module(override=None),
            'Driftkings.core.battle_events': module(battleEvents=None),
            'Driftkings.core.panel_model': module(Roster=self.roster),
            'Driftkings.settings.settings_data': settings_data,
            'Driftkings.common': module(getStatisticColor=lambda *args: '#FFFFFF'),
        })
        self.view = self.api['RatingViews'](self.config, module(getPlayersInfo=lambda ident: {}))

    def test_region_uses_client_realm_for_all_three_screens_and_cached_rows(self):
        # This account ID belongs to NA; it must not override the client's realm.
        for region in ('EU', 'NA', 'ASIA', 'CT'):
            self.api['CURRENT_REALM'] = region
            row = self.view.rows()[0]
            for screen in (row['panels']['large'], row['loading'], row['tab']):
                self.assertEqual(screen['format'], region + ' / Destroyed')
            self.assertIs(self.view.rows()[0], row)

    def test_language_changes_invalidate_cached_screens_and_extra_fields(self):
        self.view.rows()
        for language in ('pt', 'de', 'fr', 'ru', 'ja', 'en'):
            text = literal_assignment('i18n/' + language + '.py', 'TEXT')['team_panels']['UI_panel_destroyed']
            self.config.i18n['UI_panel_destroyed'] = text
            row = self.view.rows()[0]
            for screen in (row['panels']['large'], row['loading'], row['tab']):
                self.assertEqual(screen['format'], 'EU / ' + text)
                self.assertEqual(screen['fields'][0]['format'], text)

    def test_every_catalog_has_a_translation_and_unknown_macro_falls_back_to_its_name(self):
        for filename in os.listdir(os.path.join(CLIENT, 'i18n')):
            if filename in ('__init__.py', 'panel.py') or not filename.endswith('.py'):
                continue
            text = literal_assignment('i18n/' + filename, 'TEXT')['team_panels']['UI_panel_destroyed']
            self.assertTrue(text.strip(), filename)
        result = self.roster().screen({'format': '{{l10n:Unknown}}'}, {'xvm-stat': ''},
                                      {'templates': {}}, 'Left')
        self.assertEqual(result['format'], 'Unknown')
