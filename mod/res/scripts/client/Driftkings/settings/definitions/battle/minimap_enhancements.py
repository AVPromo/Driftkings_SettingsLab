# -*- coding: utf-8 -*-
import json

from Driftkings._constants import GLOBAL, MINIMAP_ENHANCEMENTS
from Driftkings.core import minimap as policy
from Driftkings.settings.controls_schema import caption, color, control, hotkey, slider
from Driftkings.settings.controls_schema import field as nested_field
from Driftkings.settings.definitions.base import SectionDefinition


class MinimapEnhancementsSettings(SectionDefinition):
    NAME = MINIMAP_ENHANCEMENTS.NAME

    TRANSLATED_TITLE = True

    def normalize_loaded(self, values):
        values[MINIMAP_ENHANCEMENTS.ARTILLERY_AIM].pop('color', None)
        policy.migrate_artillery_aim(values)
        if not values.get(MINIMAP_ENHANCEMENTS.MINIMAP_SCHEMA):
            for item in values[MINIMAP_ENHANCEMENTS.CIRCLES].values():
                item['alpha'] = values[GLOBAL.ALPHA]
            values[MINIMAP_ENHANCEMENTS.MINIMAP_SCHEMA] = 1
        policy.validate(values)
        return values

    def normalize_changes(self, values, changes):
        if isinstance(values.get(MINIMAP_ENHANCEMENTS.EXTRA_CIRCLES), (str, type(u''))):
            values[MINIMAP_ENHANCEMENTS.EXTRA_CIRCLES] = json.loads(values[MINIMAP_ENHANCEMENTS.EXTRA_CIRCLES])
        policy.validate(values)
        return values

    def getControlColumns(self):
        xColorDrawRange = color(MINIMAP_ENHANCEMENTS.COLOR_DRAW_CIRCLE, 'colorDrawCircleCheck')
        xColorMaxRange = color(MINIMAP_ENHANCEMENTS.COLOR_MAX_VIEW_CIRCLE, 'colorMaxViewCircleCheck')
        xColorMinSpottingRange = color(MINIMAP_ENHANCEMENTS.COLOR_MIN_SPOTTING_CIRCLE, 'colorMinSpottingCircleCheck')
        xColorViewRange = color(MINIMAP_ENHANCEMENTS.COLOR_VIEW_CIRCLE, 'colorViewCircleCheck')

        columns = (
            [
                control(MINIMAP_ENHANCEMENTS.PERMANENT_MINIMAP_DEATH),
                control(MINIMAP_ENHANCEMENTS.SHOW_NAMES),
                hotkey(MINIMAP_ENHANCEMENTS.BUTTON),
                control(MINIMAP_ENHANCEMENTS.VIEW_RADIUS),
                control(MINIMAP_ENHANCEMENTS.YAW),
                control(MINIMAP_ENHANCEMENTS.SHOW_LAST_POSITIONS),
                slider(MINIMAP_ENHANCEMENTS.LAST_POSITION_DURATION, 0, 300, 5, '{{value}}.s')
            ],
            [
                control(MINIMAP_ENHANCEMENTS.CHANGE_COLOR_CIRCLES),
                xColorDrawRange,
                xColorMaxRange,
                xColorMinSpottingRange,
                xColorViewRange,
                control(MINIMAP_ENHANCEMENTS.SHOW_VEHICLE_TYPES),
                slider(MINIMAP_ENHANCEMENTS.ZOOM_FACTOR_MAX, 1.0, 3.0, 0.1, '{{value}}.Px/Py')
            ]
        )

        # These controls configure only the opt-in sample until native parity is verified.
        columns[0][0:0] = [
            caption('Tactical Minimap V2'),
            nested_field(['tacticalPresentationTrial'], 'Training only: test native presentation restoration (3 seconds)'),
            nested_field(['minimapMode'], 'Minimap renderer', 'Dropdown',
                         choices=['vanilla', 'driftkings'], choice_labels=['Vanilla', 'Driftkings (preview)']),
            caption('Driftkings replacement is not available yet. Vanilla remains active.'),
            caption('The tactical preferences below apply only to the diagnostic sample.'),
            nested_field(['tactical', 'theme'], 'Tactical theme', 'Dropdown',
                         choices=['dark', 'military', 'minimal'],
                         choice_labels=['Dark Tactical', 'Military Green', 'Minimal']),
            nested_field(['tactical', 'followNativeSize'], 'Follow native minimap size'),
            nested_field(['tactical', 'size'], 'Tactical size', 'Slider', 160, 640, step=20)
        ]
        for key, title, low, high, step in (
                ('mapOpacity', 'Map opacity', 0, 1, .05),
                ('iconScale', 'Icon scale', .5, 3, .1),
                ('fontSize', 'Font size', 8, 24, 1)):
            columns[0].append(nested_field(['tactical', key], title, 'Slider', low, high, step=step))
        for key, title in (('showGrid', 'Show tactical grid'), ('showVehicleNames', 'Show vehicle names')):
            columns[0].append(nested_field(['tactical', key], title))
        for key, title in (('allyColor', 'Allies'), ('enemyColor', 'Enemies'), ('platoonColor', 'Platoon')):
            columns[0].append(nested_field(['tactical', key], title, 'ColorChoice'))

        def nested(section, key, kind='CheckBox', low=None, high=None, choices=None):
            title = self.i18n.get('UI_setting_' + section + '_' + key + '_text', key)
            labels = [self.i18n.get('UI_mode_' + value, value) for value in choices] if choices else None
            return nested_field([section, key], title, kind, low, high, choices, choice_labels=labels)
        columns[0].append(slider(MINIMAP_ENHANCEMENTS.ZOOM_FACTOR, 1.0, 3.0, 0.1, '{{value}}'))
        columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, GLOBAL.ENABLED))
        for key in ('normal', 'alternative', 'dead', 'lost'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, key, 'TextInput'))
        for key, low, high in (('fontSize', 8, 24), (GLOBAL.ALPHA, 0, 100)):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, key, 'Slider', low, high))
        for key in ('direction', 'sector'):
            columns[1].append(nested(MINIMAP_ENHANCEMENTS.LINES, key, 'Dropdown', choices=['client', 'on', 'off']))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.LINES, 'customStyle'))
        for key in ('directionColor', 'sectorColor'):
            columns[1].append(nested(MINIMAP_ENHANCEMENTS.LINES, key, 'ColorChoice'))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.LINES, GLOBAL.ALPHA, 'Slider', 0, 100))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.ARTILLERY_AIM, GLOBAL.ENABLED))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.ARTILLERY_AIM, 'scale', 'Slider', 10, 200))
        paths = policy.artillery_aim_choices(self.data[MINIMAP_ENHANCEMENTS.ARTILLERY_AIM]['src'])
        aim = nested_field([MINIMAP_ENHANCEMENTS.ARTILLERY_AIM, 'src'],
                           self.i18n['UI_setting_artilleryAim_src_text'], 'Dropdown',
                           choices=paths, previewImage=True)
        for index, option in enumerate(aim['options']):
            option['image'] = paths[index]
            option['label'] = self.i18n.get('UI_minimapAim_%d' % index, paths[index].rsplit('/', 1)[-1])
        columns[1].append(aim)
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.ARTILLERY_AIM, GLOBAL.ALPHA, 'Slider', 0, 100))
        for key in policy.CIRCLES:
            for field, kind in (('mode', 'Dropdown'), (GLOBAL.ALPHA, 'Slider')):
                item = nested(MINIMAP_ENHANCEMENTS.CIRCLES, key, kind, 0 if field == GLOBAL.ALPHA else None, 100,
                               ['client', 'on', 'off'] if field == 'mode' else None)
                item['path'].append(field)
                item['varName'] += '.' + field
                item['text'] += ' / ' + self.i18n.get('UI_field_' + field, field)
                columns[1].append(item)
        for key in ('alternativeEnabled', 'zoom', 'center'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.PRESENTATION, key))
        for key, low, high in (('sizeIndex', 0, 5), ('normalAlpha', 10, 100), ('alternativeAlpha', 10, 100), ('backgroundAlpha', 0, 100)):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.PRESENTATION, key, 'Slider', low, high))
        for key in ('ally', 'enemy', 'squad', 'alternativeAlly', 'alternativeEnemy', 'alternativeSquad'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, key, 'TextInput'))
        for key in ('x', 'y'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, key, 'Slider', -100, 100))
        columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, 'align', 'Dropdown', choices=['left', 'center', 'right']))
        for key in ('shadow', 'customColors', 'avoidOverlap'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, key))
        for key in ('allyColor', 'enemyColor', 'squadColor', 'deadColor'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, key, 'ColorChoice'))
        columns[0].append(nested(MINIMAP_ENHANCEMENTS.LABELS, 'compactLength', 'Slider', 4, 40))
        for key in ('scale', 'selfScale'):
            item = nested(MINIMAP_ENHANCEMENTS.ICONS, key, 'Slider', .5, 3)
            item['snapInterval'] = .1
            columns[0].append(item)
        for key in (GLOBAL.ALPHA, 'selfAlpha'):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.ICONS, key, 'Slider', 0, 100))
        columns[0].append(nested(MINIMAP_ENHANCEMENTS.ICONS, 'selfColor', 'ColorChoice'))
        columns[0].append(nested(MINIMAP_ENHANCEMENTS.HEALTH, 'visibility', 'Dropdown', choices=['never', 'key', 'always']))
        columns[0].append(nested(MINIMAP_ENHANCEMENTS.HEALTH, 'mode', 'Dropdown', choices=['value', 'percent', 'bar']))
        for key, low, high in (('x', -100, 100), ('y', -100, 100), ('width', 10, 100), ('height', 1, 10), ('fontSize', 8, 24)):
            columns[0].append(nested(MINIMAP_ENHANCEMENTS.HEALTH, key, 'Slider', low, high))
        for key in ('showSeconds', 'fade'):
            columns[1].append(nested(MINIMAP_ENHANCEMENTS.LOST_MARKER, key))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.LOST_MARKER, 'minimumAlpha', 'Slider', 0, 100))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.MAP_SIZE, GLOBAL.ENABLED))
        for key, low, high in (('x', -300, 300), ('y', -300, 300), ('fontSize', 8, 24)):
            columns[1].append(nested(MINIMAP_ENHANCEMENTS.MAP_SIZE, key, 'Slider', low, high))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.MAP_SIZE, 'color', 'ColorChoice'))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.MAP_SIZE, 'format', 'TextInput'))
        columns[1].append(nested(MINIMAP_ENHANCEMENTS.LINES, 'geometry'))
        for key, low, high in (('length', 50, 1500), ('thickness', 1, 5), ('dash', 0, 100), ('gap', 1, 100)):
            columns[1].append(nested(MINIMAP_ENHANCEMENTS.LINES, key, 'Slider', low, high))
        for circle in policy.CIRCLES:
            for key, low, high in (('thickness', 1, 5), ('dash', 0, 100), ('gap', 1, 100)):
                item = nested(MINIMAP_ENHANCEMENTS.CIRCLES, circle, 'Slider', low, high)
                item['path'].append(key)
                item['varName'] += '.' + key
                item['text'] += ' / ' + self.i18n.get('UI_setting_lines_' + key + '_text', key)
                columns[1].append(item)
        columns[1].append(nested_field([MINIMAP_ENHANCEMENTS.EXTRA_CIRCLES],
                         self.i18n.get('UI_setting_extraCircles_text', 'Extra circles (JSON)'),
                         'TextInput', jsonValue=True))
        return columns
