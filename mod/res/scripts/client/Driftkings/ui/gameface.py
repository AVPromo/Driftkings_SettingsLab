# -*- coding: utf-8 -*-
"""Owned UI lifecycle connected to the Gameface dependency required by ModList."""
import json

from frameworks.wulf import ViewModel
from gui.impl.gen import R
from openwg_gameface import gf_mod_inject

# WG's native invalid resource sentinel; gui.impl.gen_utils was removed.
INVALID_RES_ID = -1

BOOTSTRAP = 'coui://gui/gameface/mods/Driftkings/shared/bootstrap.js'


def resource_id(key):
    # WG 2.4.1 loads gui/gen_resources declarations into the native R tree.
    # Keep the existing callers' slash-separated keys within our own subtree.
    parts = key.split('/')
    if len(parts) != 4 or parts[:2] != ['mods', 'Driftkings'] or not all(parts):
        raise ValueError('Unknown Driftkings resource key: ' + key)
    accessor = R
    for part in parts:
        accessor = getattr(accessor, part)
    return accessor()


class AssetsModel(ViewModel):
    def __init__(self, name, styles, scripts):
        self._name = name
        self._styles = json.dumps(styles or [])
        self._scripts = json.dumps(scripts or [])
        super(AssetsModel, self).__init__(properties=3, commands=0)

    def _initialize(self):
        super(AssetsModel, self)._initialize()
        self._addStringProperty('name', self._name)
        self._addStringProperty('styles', self._styles)
        self._addStringProperty('scripts', self._scripts)


def attach_assets(model, name, styles=None, scripts=None):
    model._addViewModelProperty('DriftkingsUI', AssetsModel(name, styles, scripts))
    # OpenWG injects only our bootstrap; it retains ordered loading and cleanup.
    gf_mod_inject(model, name + 'Bridge', scripts=[BOOTSTRAP])
