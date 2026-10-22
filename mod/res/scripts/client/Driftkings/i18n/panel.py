# -*- coding: utf-8 -*-
"""Interface catalogs; English is complete and the fallback for every key.

Add a language with PANEL and register it in Driftkings.locale_support.
Optional overrides: <config root>/locales/<code>.json (strings only).
"""
import json
from Driftkings.logger import get_logger
import os

from Driftkings.locale_support import LANGUAGES, language_code as normalize

logger = get_logger('Driftkings.i18n.panel')
try:
    text_types = (str, unicode)
except NameError:
    text_types = (str,)


def is_text(value):
    return isinstance(value, text_types)

def _catalog(code):
    module = __import__('Driftkings.i18n.' + code, fromlist=['PANEL'])
    return dict(module.PANEL)


def load(language, override_root=None):
    code = normalize(language)
    strings = _catalog('en')
    if code != 'en':
        strings.update(_catalog(code))
    if override_root:
        path = os.path.join(override_root, 'locales', code + '.json')
        if os.path.isfile(path):
            try:
                with open(path, 'rb') as stream:
                    extra = json.loads(stream.read().decode('utf-8-sig'))
                if isinstance(extra, dict):
                    strings.update(dict((k, v) for k, v in extra.items() if is_text(k) and is_text(v)))
            except (IOError, OSError, ValueError) as error:
                logger.warning('Ignored invalid locale override %s: %s', path, error)
    return code, strings


def translations(key):
    """{language: text} for a catalog key, for labels of built-in pages."""
    return dict((code, _catalog(code).get(key, _catalog('en').get(key, key))) for code, _ in LANGUAGES)
