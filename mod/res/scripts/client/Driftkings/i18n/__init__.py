# -*- coding: utf-8 -*-
"""One catalog per language, with unified optional JSON overrides."""
import copy
import importlib
import json
from Driftkings.logger import get_logger
import os

from Driftkings.locale_support import language_code
from Driftkings.settings.sections import previous_name, section_name, section_aliases
from Driftkings.settings.store import SettingsStore, merge, recover_file

LOG = get_logger('Driftkings.i18n')


def read_catalog(path):
    with open(path, 'rb') as stream:
        value = json.loads(stream.read().decode('utf-8-sig'))
    if not isinstance(value, dict) or any(not isinstance(section, dict) for section in value.values()):
        raise ValueError('Expected a catalog with component sections: ' + path)
    return value


def client_text(value):
    # Preserve the UTF-8 strings expected by the existing Python 2 client APIs.
    try:
        text_type = unicode
    except NameError:
        return value
    if isinstance(value, text_type):
        return value.encode('utf-8')
    if isinstance(value, dict):
        return dict((client_text(key), client_text(text)) for key, text in value.items())
    if isinstance(value, list):
        return [client_text(text) for text in value]
    return value


def canonical_sections(document):
    # Older overrides keep their original file and section names on disk.
    # Explicit canonical sections take precedence if both spellings exist.
    result = {}
    for canonical in (False, True):
        for name, values in document.items():
            if (section_name(name) == name) == canonical:
                section = section_name(name)
                values = dict(values)
                # Retire copied internal identifiers as display titles; keep custom titles.
                if values.get('UI_description') in section_aliases(section):
                    values.pop('UI_description', None)
                result[section] = merge(result.get(section, {}), values)
    return result


class TranslationCatalog(object):
    def __init__(self, root='./mods/configs/Driftkings'):
        self.root = os.path.abspath(root)
        self.cache = {}

    def bundled(self, language):
        english = importlib.import_module('Driftkings.i18n.en').TEXT
        if language == 'en':
            return copy.deepcopy(english)
        return merge(english, importlib.import_module('Driftkings.i18n.' + language).TEXT)

    def migrate(self, language, components, path):
        sections = {}
        for component in components:
            legacy = os.path.join(self.root, previous_name(component), 'i18n', language + '.json')
            if not os.path.isfile(legacy):
                continue
            try:
                with open(legacy, 'rb') as stream:
                    value = json.loads(stream.read().decode('utf-8-sig'))
                if not isinstance(value, dict):
                    raise ValueError('Expected an object')
                sections[component] = value
            except (ValueError, IOError) as error:
                # Do not mark migration complete when a source could not be read.
                raise ValueError('Could not import translations from %s: %s' % (legacy, error))
        SettingsStore(path).write(sections)

    def read(self, language):
        language = language_code(language)
        path = os.path.join(self.root, 'i18n', language + '.json')
        try:
            recover_file(path)
            if not os.path.isfile(path):
                self.migrate(language, self.bundled(language), path)
            stat = os.stat(path)
            signature = (stat.st_mtime, stat.st_size)
            if language not in self.cache or self.cache[language][0] != signature:
                overrides = canonical_sections(read_catalog(path))
                self.cache[language] = (signature, merge(self.bundled(language), overrides))
            return self.cache[language][1]
        except (ValueError, IOError, OSError):
            LOG.exception('Could not load translation overrides: %s', path)
            return self.bundled(language)

    def section(self, component, language='en'):
        component = section_name(component)
        catalog = self.read(language)
        return client_text(merge(catalog.get('common', {}), catalog.get(component, {'UI_description': component})))


catalog = TranslationCatalog()
