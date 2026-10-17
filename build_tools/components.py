"""Read the single component manifest using canonical runtime section names."""
import json
from pathlib import Path
import re


FIELDS = {'kind', 'enabled', 'entrypoint', 'config_files', 'assets'}


def read_components(root, source):
    root = Path(root).resolve()
    if not isinstance(source, str) or Path(source).is_absolute() or '\\' in source or ':' in source:
        raise ValueError('Expected a relative component manifest path')
    path = root / source
    if any(part in ('', '.', '..') for part in source.split('/')) or not path.resolve().is_relative_to(root):
        raise ValueError('Component manifest path escapes repository')

    def unique_pairs(items):
        result = {}
        for name, value in items:
            if name in result:
                raise ValueError('Duplicate component manifest key: ' + name)
            result[name] = value
        return result

    document = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_pairs)
    if (not isinstance(document, dict) or set(document) != {'schema_version', 'components'} or
            type(document['schema_version']) is not int or document['schema_version'] != 1 or
            not isinstance(document['components'], dict) or not document['components']):
        raise ValueError('Invalid unified component manifest schema')
    manifests = []
    for name, item in sorted(document['components'].items()):
        if re.fullmatch(r'[a-z][a-z0-9]*(?:_[a-z0-9]+)*', name) is None:
            raise ValueError('Component must use its canonical name: ' + name)
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise ValueError('Invalid component fields: ' + name)
        if item['kind'] == 'feature':
            entrypoint = item['entrypoint']
            if not isinstance(entrypoint, str) or entrypoint.split('.')[-1] != name:
                raise ValueError('Component name differs from its runtime module: ' + name)
        manifests.append(dict(item, schema_version=1, id=name))
    return manifests
