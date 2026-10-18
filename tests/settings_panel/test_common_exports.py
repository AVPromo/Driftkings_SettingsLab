# -*- coding: utf-8 -*-
"""Check the public common facade without starting BigWorld or its GUI."""
import ast
import os
import re
import types
import unittest

from test_values import CLIENT, load_source


class CommonExportsTests(unittest.TestCase):
    def test_explicit_exports_preserve_the_previous_facade(self):
        names = ('abstract', 'chat', 'colorRatting', 'game', 'iter', 'logger', 'monkeypatch', 'wgUtils')
        package = types.ModuleType('utils')
        package.events = object()
        bigworld = types.ModuleType('BigWorld')
        dependencies = {'BigWorld': bigworld, 'Driftkings.common.utils': package}
        expected = {'BigWorld': bigworld, 'events': package.events}
        for name in names:
            path = os.path.join(CLIENT, 'common', 'utils', name + '.py')
            with open(path, 'rb') as stream:
                source = stream.read().decode('utf-8')
            exported = ast.literal_eval(re.search(r'__all__\s*=\s*(\(.*?\))', source, re.S).group(1))
            module = types.ModuleType(name)
            for symbol in exported:
                if not hasattr(module, symbol):
                    setattr(module, symbol, object())
                expected[symbol] = getattr(module, symbol)
            setattr(package, name, module)
            dependencies['Driftkings.common.utils.' + name] = module
            expected[name] = module
        utilities = load_source('common/utils/__init__.py', dependencies)
        self.assertEqual(set(utilities['__all__']), set(expected))
        for name, value in expected.items():
            self.assertIs(utilities[name], value)

    def test_all_common_imports_used_by_runtime_are_explicitly_available(self):
        path = os.path.join(CLIENT, 'common', '__init__.py')
        with open(path, 'rb') as stream:
            tree = ast.parse(stream.read(), path)
        exported = {'curCV'}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                exported.update(alias.asname or alias.name for alias in node.names)
            elif isinstance(node, ast.Import):
                exported.update(alias.asname or alias.name.split('.')[0] for alias in node.names)
        for folder, dirs, files in os.walk(CLIENT):
            for name in files:
                if not name.endswith('.py'):
                    continue
                path = os.path.join(folder, name)
                with open(path, 'rb') as stream:
                    source = stream.read().decode('utf-8-sig')
                for match in re.finditer(r'^from Driftkings\.common import (.+)$', source, re.M):
                    imported = [name.strip().split(' as ')[0] for name in match.group(1).split(',')]
                    self.assertTrue(set(imported).issubset(exported), (path, imported))


if __name__ == '__main__':
    unittest.main()
