# -*- coding: utf-8 -*-
from Driftkings._constants import THIRD_PERSON_ZOOM
from Driftkings.core.camera_settings import validate
from Driftkings.settings.controls_schema import field
from Driftkings.settings.definitions.base import SectionDefinition


class ThirdPersonZoomSettings(SectionDefinition):
    NAME = THIRD_PERSON_ZOOM.NAME
    TRANSLATED_TITLE = True

    def getControlColumns(self):
        columns = [[], []]
        for mode in ('arcade', 'postmortem', 'strategic', 'arty'):
            column = columns[0 if mode in ('arcade', 'postmortem') else 1]
            title = self.i18n['UI_camera_' + mode] + ': '
            if mode in ('strategic', 'arty'):
                column.append(field([mode, 'useClientDefaults'], title + self.i18n['UI_camera_native']))
            for key, low, high in (('min', 1, 450), ('max', 1, 450), ('scrollSensitivity', 1, 100)):
                column.append(field([mode, key], title + self.i18n['UI_setting_' + key + '_text'],
                                    'Slider', low, high, step=1))
            if mode in ('arcade', 'postmortem'):
                column.append(field([mode, 'startDist'], title + self.i18n['UI_setting_startDeadDist_text'],
                                    'Slider', 1, 450, step=1))
        return columns

    def normalize_loaded(self, values):
        return validate(values)

    def normalize_changes(self, values, changes):
        return validate(values)
