# -*- coding: utf-8 -*-
"""Engine-free reader for flat, string-only localization YML files.

Keys are component.key or panel.key. Double-quoted values use JSON escaping,
a YAML subset that preserves Unicode, HTML, whitespace and literal backslashes.
Plain text and YAML single-quoted strings are also accepted. No YAML execution,
objects, nesting or external parser dependency is involved.
"""
import json
import re

try:
    text_type = unicode
except NameError:
    text_type = str


def parse_catalog(content):
    if not isinstance(content, text_type):
        content = content.decode('utf-8-sig')
    content = content.lstrip(u'\ufeff')
    result = {'TEXT': {}, 'PANEL': {}}
    seen = set()
    for number, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, separator, value = line.partition(': ')
        if not separator or not re.match(r'^[A-Za-z_][A-Za-z0-9_.-]*\Z', key):
            raise ValueError('Invalid locale entry at line %s' % number)
        if key in seen:
            raise ValueError('Duplicate locale key at line %s: %s' % (number, key))
        seen.add(key)
        section, separator, name = key.partition('.')
        if not separator or not name:
            raise ValueError('Expected component.key or panel.key at line %s' % number)
        value = value.strip()
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'"):
            if not value.endswith("'") or len(value) < 2:
                raise ValueError('Unclosed string at line %s' % number)
            value = value[1:-1].replace("''", "'")
        else:
            value = value.replace('\\n', '\n')
        if not isinstance(value, text_type):
            raise ValueError('Expected text at line %s' % number)
        if section == 'panel':
            result['PANEL'][name] = value
        else:
            target = result['TEXT'].setdefault(section, {})
            parts = name.split('.')
            if not all(parts):
                raise ValueError('Empty locale key segment at line %s' % number)
            for part in parts[:-1]:
                target = target.setdefault(part, {})
                if not isinstance(target, dict):
                    raise ValueError('Conflicting locale key at line %s' % number)
            if parts[-1] in target:
                raise ValueError('Conflicting locale key at line %s' % number)
            target[parts[-1]] = value
    return result
