# -*- coding: utf-8 -*-
"""Carousel PNGs from the resource tree mounted by the client's .wotmod loader."""
import base64
from driftkings.logger import get_logger
import os
import re

LEGACY_ROOT = 'mods/driftkings/Carroucel/'
RESOURCE_ROOT = 'gui/maps/driftkings/Carroucel/'
ICON_PATH = re.compile(r'(?:(?:coui|img)://)?gui/maps/driftkings/Carroucel/[#A-Za-z0-9_-]+\.png|mods/driftkings/Carroucel/[#A-Za-z0-9_-]+\.png')
MAX_IMAGE_SIZE = 2 * 1024 * 1024


class CarouselImages(object):
    def __init__(self, root=None):
        # Explicit resource root for offline tools; the game always uses ResMgr.
        self.root = os.path.realpath(root) if root is not None else None
        self.cache = {}
        self.missing = set()

    def resolve(self, path):
        if not ICON_PATH.match(path) or ICON_PATH.match(path).group(0) != path:
            return ''
        resource = path.split('://', 1)[-1]
        if resource.startswith(LEGACY_ROOT):
            resource = RESOURCE_ROOT + resource[len(LEGACY_ROOT):]
        if resource in self.cache:
            return self.cache[resource]
        try:
            try:
                import ResMgr
            except ImportError:
                data = None
                if self.root is not None:
                    with open(os.path.join(self.root, resource), 'rb') as stream:
                        data = stream.read(MAX_IMAGE_SIZE + 1)
            else:
                section = ResMgr.openSection(resource)
                data = section.asBinary if section is not None else None
        except (IOError, OSError, ValueError):
            data = None
        if data and len(data) <= MAX_IMAGE_SIZE and data.startswith(b'\x89PNG\r\n\x1a\n'):
            result = 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')
            if len(self.cache) >= 32:
                self.cache.clear()
            self.cache[resource] = result
            self.missing.discard(path)
            return result
        if path not in self.missing:
            self.missing.add(path)
            get_logger('Driftkings.CarouselStats').warning('Packaged carousel icon not found: %s', resource)
        return ''

    def collect(self, vehicles):
        paths = set()
        for profiles in vehicles.values():
            for profile in profiles.values():
                for field in profile.get('extraFields', ()):
                    if field.get('showIcons', True):
                        for key in ('src', 'format'):
                            paths.update(ICON_PATH.findall(field.get(key, '')))
        return dict((path, self.resolve(path)) for path in sorted(paths))
