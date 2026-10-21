# -*- coding: utf-8 -*-
try:
    import Queue as queue
except ImportError:
    import queue

from support import RuntimeTest, module, source


class PlayerRatingsTests(RuntimeTest):
    def setUp(self):
        super(PlayerRatingsTests, self).setUp()
        colors = self.load('common.utils.colorRatting')
        self.api = source('core/player_ratings.py', {
            'urllib2': module(), 'Queue': queue,
            'gui.battle_control.arena_info.interfaces': module(IArenaVehiclesController=object),
            'gui.battle_control.arena_info.settings': module(ARENA_LISTENER_SCOPE=module(VEHICLES=2)),
            'gui.battle_control.battle_constants': module(BATTLE_CTRL_ID=module(MOD=19)),
            'gui.shared.gui_items.Vehicle': module(getVehicleClassTag=lambda value: None),
            'gui.shared.personality': module(ServicesLocator=object()),
            'helpers': module(dependency=module(descriptor=lambda value: None)),
            'messenger': module(g_settings=object()),
            'skeletons.gui.battle_session': module(IBattleSessionProvider=object),
            'Driftkings._constants': module(GLOBAL=object(), TEAM_PANELS=object()),
            'Driftkings.common.utils.wgUtils': module(getPlayer=lambda: None, logWarning=lambda *args: None,
                                       getStatisticColor=colors.getStatisticColor,
                                       callback=lambda *args: None, cancelCallback=lambda *args: None),
            'Driftkings.common.utils.colorRatting': module(getPlayer=lambda: None, logWarning=lambda *args: None,
                                       getStatisticColor=colors.getStatisticColor,
                                       callback=lambda *args: None, cancelCallback=lambda *args: None),
            'Driftkings.core.callbacks': module(getPlayer=lambda: None, logWarning=lambda *args: None,
                                       getStatisticColor=colors.getStatisticColor,
                                       callback=lambda *args: None, cancelCallback=lambda *args: None),
            'Driftkings.core.hooks': module(override=lambda *args: None),
            'Driftkings.settings.service': module(settings_service=object()),
            'Driftkings.stats.vehinfo': module(calculateXvmScale=lambda metric, value: value,
                                      getVehicleInfoData=lambda value: None, scaleValuesInstance=object())})

    def test_unavailable_ratings_have_missing_marker_and_neutral_color(self):
        result = self.api['format_rating']('{{wn8}} {{c:wn8}} {{r}}', {}, {}, False)
        self.assertEqual(result, u'\u2014 #AAAAAA \u2014')

    def test_available_ratings_use_the_configured_palette(self):
        colors = self.load('common.utils.colorRatting')
        for index in range(3):
            result = self.api['format_rating']('{{wn8}} {{c:wn8}}', {'wn8': 2000}, {}, True, index)
            self.assertEqual(result, '2000 ' + colors.getStatisticColor('wn8', 2000, index))

    def test_names_are_escaped_and_macros_do_not_traverse_objects(self):
        result = self.api['format_rating']('{{name}} {{clan}}', {}, {'name': '<Admin>', 'clanAbbrev': 'A&B'}, True)
        self.assertEqual(result, '&lt;Admin&gt; [A&amp;B]')
        formatter = self.api['RatingFormatter']()
        self.assertEqual(formatter.vformat('{name.__class__}', (), {'name': 'unsafe'}), u'\u2014')

    def test_damage_ratio_missing_denominators_and_valid_value(self):
        ratio = self.api['tank_damage_ratio']
        for battles, hp, damage in ((0, 100, 100), (-1, 100, 100), (2, 0, 100), (2, -1, 100), (2, 100, None)):
            self.assertEqual(ratio({'battles': battles, 'damage_dealt': damage}, hp), u'\u2014')
        self.assertEqual(ratio({'battles': 4, 'damage_dealt': 6000}, 1000), 1.5)
