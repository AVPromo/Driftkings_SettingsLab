# -*- coding: utf-8 -*-
"""Carousel PNGs from external overrides or packaged resources."""
import base64
import logging
import os
import re

ICON_ROOT = 'mods/Driftkings/Carroucel/'
ICON_PATH = re.compile(r'mods/Driftkings/Carroucel/[#A-Za-z0-9_-]+\.png')
MAX_IMAGE_SIZE = 2 * 1024 * 1024
RESOURCE_ROOT = 'gui/maps/Driftkings/Carroucel/'


class CarouselImages(object):
    def __init__(self, root=None):
        self.root = os.path.realpath(root or os.getcwd())
        self.cache = {}
        self.missing = set()

    def resolve(self, path):
        if not ICON_PATH.match(path) or ICON_PATH.match(path).group(0) != path:
            return ''
        absolute = os.path.realpath(os.path.join(self.root, path))
        allowed = os.path.realpath(os.path.join(self.root, ICON_ROOT)) + os.sep
        if not os.path.normcase(absolute).startswith(os.path.normcase(allowed)):
            return ''
        try:
            stat = os.stat(absolute)
            signature = (stat.st_mtime, stat.st_size)
            cached = self.cache.get(path)
            if cached and cached[0] == signature:
                return cached[1]
            if stat.st_size > MAX_IMAGE_SIZE:
                return ''
            with open(absolute, 'rb') as stream:
                data = stream.read(MAX_IMAGE_SIZE + 1)
            if len(data) > MAX_IMAGE_SIZE or not data.startswith(b'\x89PNG\r\n\x1a\n'):
                return ''
            result = 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')
            if len(self.cache) >= 32:
                self.cache.clear()
            self.cache[path] = (signature, result)
            self.missing.discard(path)
            return result
        except (IOError, OSError):
            resource = RESOURCE_ROOT + path[len(ICON_ROOT):]
            cached = self.cache.get(resource)
            if cached is not None:
                return cached
            try:
                import ResMgr
                section = ResMgr.openSection(resource)
                data = section.asBinary if section is not None else None
            except ImportError:
                # Local tools read the same res tree without the client API.
                try:
                    with open(os.path.join(self.root, resource), 'rb') as stream:
                        data = stream.read(MAX_IMAGE_SIZE + 1)
                except (IOError, OSError):
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
                logging.getLogger('Driftkings.CarouselStats').warning('Carousel icon not found: %s', path)
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
