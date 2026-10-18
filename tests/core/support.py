# -*- coding: utf-8 -*-
"""Load real portable modules without executing the game's package facades."""
import importlib
import os
import sys
import types
import unittest
try:
    import builtins
except ImportError:
    import __builtin__ as builtins

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT = os.path.join(ROOT, 'mod', 'res', 'scripts', 'client', 'Driftkings')


def module(**values):
    result = types.ModuleType('test_stub')
    result.__dict__.update(values)
    return result


class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.saved = dict((key, value) for key, value in sys.modules.items()
                          if key == 'Driftkings' or key.startswith('Driftkings.'))
        self.addCleanup(self.restore_modules)
        for key in self.saved:
            del sys.modules[key]
        for name, relative in (('Driftkings', ''), ('Driftkings.core', 'core'),
                               ('Driftkings.common', 'common'), ('Driftkings.common.utils', 'common/utils')):
            package = types.ModuleType(name)
            package.__path__ = [os.path.join(CLIENT, *relative.split('/'))]
            sys.modules[name] = package
        sys.modules['Driftkings'].VERSION = '1.0.0'

    def restore_modules(self):
        for key in list(sys.modules):
            if key == 'Driftkings' or key.startswith('Driftkings.'):
                del sys.modules[key]
        sys.modules.update(self.saved)

    def load(self, relative):
        return importlib.import_module('Driftkings.' + relative)


def source(relative, dependencies):
    """Stub import boundaries only; execute the entire production source."""
    original = builtins.__import__

    def importing(name, globals=None, locals=None, fromlist=(), level=0):
        if name in dependencies:
            return dependencies[name]
        return original(name, globals, locals, fromlist, level)

    api = dict(vars(builtins))
    api['__import__'] = importing
    path = os.path.join(CLIENT, *relative.split('/'))
    namespace = {'__name__': '_core_test', '__file__': path, '__builtins__': api}
    with open(path, 'rb') as stream:
        eval(compile(stream.read(), path, 'exec'), namespace)
    return namespace
