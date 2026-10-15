# -*- coding: utf-8 -*-
import ResMgr


def read_config_dir(owner, quiet, recursive=False, dir_name='configs', error_not_exist=True, make_dir=True, ordered=False, encrypted=False, migrate=False, ext='.json', _globals=None):
    if _globals is None:
        _globals = globals()
    configs_dir = owner.configPath + dir_name + '/'
    if not _globals['os'].path.isdir(configs_dir):
        if error_not_exist and not quiet:
            print('=' * 30)
            print(owner.LOG, 'config directory not found:', configs_dir)
            print('=' * 30)
        if make_dir:
            _globals['os'].makedirs(configs_dir)
    for dir_path, sub_dirs, names in _globals['os'].walk(configs_dir):
        dir_path = dir_path.replace('\\', '/').decode('windows-1251').encode('utf-8')
        local_path = dir_path.replace(configs_dir, '')
        names = sorted([x for x in names if x.endswith(ext)], key=str.lower)
        if not recursive:
            sub_dirs[:] = []
        for name in names:
            name = _globals['os'].path.splitext(name)[0].decode('windows-1251').encode('utf-8')
            json_data = {}
            try:
                if ext == '.json':
                    if ordered:
                        json_data = _globals['loadJsonOrdered'](owner.ID, dir_path, name)
                    else:
                        json_data = _globals['loadJson'](owner.ID, name, json_data, dir_path, encrypted=encrypted)
                elif ext == '.xml':
                    json_data = _globals['ResMgr'].openSection('.' + dir_path + '/' + name + ext)
            except Exception:
                _globals['traceback'].print_exc()
            if not json_data:
                print(owner.LOG, (dir_path and (dir_path + '/')) + name + ext, 'is invalid')
                continue
            try:
                if ext == '.json':
                    if migrate:
                        owner.onMigrateConfig(quiet, dir_path, local_path, name, json_data, sub_dirs, names)
                    else:
                        owner.onReadConfig(quiet, local_path, name, json_data, sub_dirs, names)
                elif ext == '.xml':
                    owner.onReadDataSection(quiet, dir_path, local_path, name, json_data, sub_dirs, names)
                    _globals['ResMgr'].purge('.' + dir_path + '/' + name + ext)
            except Exception:
                _globals['traceback'].print_exc()
