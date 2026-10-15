# -*- coding: utf-8 -*-
class ConfigNoInterface(object):
    def createTemplate(self):
        pass


def _config_namespace():
    import sys
    module = sys.modules.get('Driftkings.common.config.interfaces.simple')
    return vars(module) if module is not None else None


def _config_dependency(namespace, name):
    if namespace is not None:
        if name in namespace:
            return namespace[name]
        builtins = namespace.get('__builtins__', {})
        if not isinstance(builtins, dict):
            builtins = vars(builtins)
        if name in builtins:
            return builtins[name]
        raise NameError("global name '%s' is not defined" % name)
    if name == 'VERSION':
        from Driftkings import VERSION
        return VERSION
    if name == 'TemplateBuilder':
        from Driftkings.settings.template_builder import TemplateBuilder
        return TemplateBuilder
    if name == 'loadJson':
        from Driftkings.common.config.json_reader import loadJson
        return loadJson
    if name == 'ConfigBase':
        return ConfigBase
    if name == 'SettingsLifecycle':
        from Driftkings.settings.lifecycle import SettingsLifecycle
        return SettingsLifecycle
    if name == 'processHotKeys':
        from Driftkings.settings.hotkeys import processHotKeys
        return processHotKeys
    if name == 'smart_update':
        from Driftkings.settings.config_utils import smart_update
        return smart_update
    if name == 'NotImplementedError':
        return NotImplementedError
    raise NameError("global name '%s' is not defined" % name)


def _component_namespace():
    import sys
    module = sys.modules.get('Driftkings.common.config.interfaces.component')
    return vars(module) if module is not None else None


def _component_dependency(namespace, name, canonical_class=None):
    if namespace is not None:
        return _config_dependency(namespace, name)
    if name == '_DRIFTKINGS_AUTHOR':
        from Driftkings._constants import DRIFTKINGS_AUTHOR
        return DRIFTKINGS_AUTHOR
    if name == '_DRIFTKINGS_MODS_GROUP':
        from Driftkings._constants import DRIFTKINGS_MODS_GROUP
        return DRIFTKINGS_MODS_GROUP
    if name == 'DriftkingsConfigInterface':
        return canonical_class
    if name == 'super':
        return super
    raise NameError("global name '%s' is not defined" % name)


class ConfigBase(object):
    def __init__(self):
        self.ID = ''
        self.defaultKeys = {}
        self.i18n = {}
        self.data = {}
        self.author = ''
        self.version = _config_dependency(_config_namespace(), 'VERSION')
        self.modsGroup = ''
        self.configPath = ''
        self.langPath = ''

    LOG = property(lambda self: self.ID + ':')
    def loadDataJson(self, *args, **kwargs):
        if self.modsGroup == 'Driftkings':
            from Driftkings.settings.store import load_config
            return load_config(self)
        from Driftkings.common.config.legacy_io import load_data
        return load_data(self, args, kwargs, _config_dependency(_config_namespace(), 'loadJson'))

    def writeDataJson(self, *args, **kwargs):
        if self.modsGroup == 'Driftkings':
            from Driftkings.settings.loader import settings_loader
            return settings_loader.save(self.ID, self.data)
        from Driftkings.common.config.legacy_io import write_data
        return write_data(self, args, kwargs, _config_dependency(_config_namespace(), 'loadJson'))

    def loadLangJson(self, *args, **kwargs):
        if self.modsGroup == 'Driftkings':
            from Driftkings.i18n import catalog
            return catalog.section(self.ID, self.lang)
        from Driftkings.common.config.legacy_io import load_lang
        return load_lang(self, args, kwargs, _config_dependency(_config_namespace(), 'loadJson'))

    def init(self):
        self.configPath = './mods/configs/%s/%s/' % (self.modsGroup, self.ID)
        self.langPath = './mods/configs/Driftkings/i18n/' if self.modsGroup == 'Driftkings' else '%si18n/' % self.configPath
        self.registerHotkeys()
        if self.modsGroup == 'Driftkings':
            from Driftkings.settings.service import settings_service
            settings_service.register(self)

    def loadLang(self):
        labels = self.loadLangJson()
        self.i18n.clear()
        self.i18n.update(labels)

    def createTB(self):
        return _config_dependency(_config_namespace(), 'TemplateBuilder')(self.data, self.i18n)

    def readConfigDir(self, quiet, recursive=False, dir_name='configs', error_not_exist=True, make_dir=True, ordered=False, encrypted=False, migrate=False, ext='.json'):
        from Driftkings.common.config.legacy_scan import read_config_dir
        read_config_dir(self, quiet, recursive, dir_name, error_not_exist, make_dir,
                        ordered, encrypted, migrate, ext, _globals=_config_namespace())

    def onMigrateConfig(self, quiet, path, dir_path, name, json_data, sub_dirs, names):
        """clearing sub_dirs and/or names using slice assignment breaks the corresponding loop"""
        pass

    def onReadConfig(self, quiet, dir_path, name, json_data, sub_dirs, names):
        """clearing sub_dirs and/or names using slice assignment breaks the corresponding loop"""
        pass

    def onReadDataSection(self, quiet, path, dir_path, name, data_section, sub_dirs, names):
        """clearing sub_dirs and/or names using slice assignment breaks the corresponding loop"""
        pass


    def onHotkeyPressed(self, event):
        pass

    def registerHotkeys(self):
        from Driftkings.core.keyboard import keyboard
        keyboard.subscribe(self.onHotkeyPressed)


class ConfigInterface(ConfigBase, _config_dependency(None, 'SettingsLifecycle')):
    def __init__(self):
        _config_dependency(_config_namespace(), 'ConfigBase').__init__(self)
        _config_dependency(_config_namespace(), 'SettingsLifecycle').__init__(self)

    def getData(self):
        return self.data

    def createTemplate(self):
        raise _config_dependency(_config_namespace(), 'NotImplementedError')

    def readData(self, quiet=True):
        _config_dependency(_config_namespace(), 'processHotKeys')(self.data, self.defaultKeys, 'write')
        try:
            _config_dependency(_config_namespace(), 'smart_update')(self.data, self.loadDataJson(quiet=quiet))
        finally:
            _config_dependency(_config_namespace(), 'processHotKeys')(self.data, self.defaultKeys, 'read')

    def onApplySettings(self, settings):
        _config_dependency(_config_namespace(), 'smart_update')(self.data, settings)
        _config_dependency(_config_namespace(), 'processHotKeys')(self.data, self.defaultKeys, 'write')
        try:
            self.writeDataJson()
        finally:
            _config_dependency(_config_namespace(), 'processHotKeys')(self.data, self.defaultKeys, 'read')


class DriftkingsConfigInterface(ConfigInterface):
    def init(self):
        self.author = _component_dependency(_component_namespace(), '_DRIFTKINGS_AUTHOR')
        self.modsGroup = _component_dependency(_component_namespace(), '_DRIFTKINGS_MODS_GROUP')
        _component_dependency(_component_namespace(), 'super')(_component_dependency(_component_namespace(), 'DriftkingsConfigInterface', DriftkingsConfigInterface), self).init()
