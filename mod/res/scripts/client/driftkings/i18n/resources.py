# -*- coding: utf-8 -*-
"""Cached localization resources shared by component and panel translations."""
import copy
import os

from driftkings.core.locale_catalog import parse_catalog
from driftkings.locale_support import language_code
from driftkings.logger import get_logger

LOG = get_logger('driftkings.i18n.resources')
RESOURCE_ROOT = 'mods/driftkings/text'


def read_resource(code):
    path = RESOURCE_ROOT + '/' + code + '.yml'
    try:
        import ResMgr
    except ImportError:
        # Standalone tests/tools use the same resources from the source tree.
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', path)
        with open(path, 'rb') as stream:
            return stream.read()
    section = ResMgr.openSection(path)
    if section is None or not ResMgr.isFile(path):
        raise IOError('Missing locale resource: ' + path)
    return section.asBinary


class CatalogResources(object):
    def __init__(self, reader=read_resource):
        self.reader = reader
        self.cache = {}

    def load(self, language):
        code = language_code(language)
        if code not in self.cache:
            try:
                document = parse_catalog(self.reader(code))
                if code == 'en' and (not document['TEXT'] or not document['PANEL']):
                    raise ValueError('English locale requires component and panel text')
            except (IOError, OSError, ValueError, UnicodeError):
                LOG.exception('Could not load bundled locale: %s', code)
                if code == 'en':
                    raise
                document = {'TEXT': {}, 'PANEL': {}}
            self.cache[code] = document
        return copy.deepcopy(self.cache[code])


resources = CatalogResources()
