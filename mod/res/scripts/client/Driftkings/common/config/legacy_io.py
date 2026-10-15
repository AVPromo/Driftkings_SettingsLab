# -*- coding: utf-8 -*-
from Driftkings.common.config.json_reader import loadJson


def load_data(owner, args, kwargs, loader=loadJson):
    return loader(owner.ID, owner.ID, owner.data, owner.configPath, *args, **kwargs)


def write_data(owner, args, kwargs, loader=loadJson):
    return loader(owner.ID, owner.ID, owner.data, owner.configPath, True, False, *args, **kwargs)


def load_lang(owner, args, kwargs, loader=loadJson):
    return loader(owner.ID, owner.lang, owner.i18n, owner.langPath, *args, **kwargs)
