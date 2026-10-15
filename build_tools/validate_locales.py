"""Check bundled catalog coverage and formatting against the English source."""
import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FORMATTING = re.compile(
    r'<[^>]*>|\{\{.*?\}\}|\{[^{}]*\}|%\([^)]+\)[#0 +\-]*[0-9.]*(?:[sdrifgeouxX])|'
    r'%(?:[0-9.]+)?[sdf]|%%|&(?:\w+|#\d+);')
PATHS = re.compile(r'[A-Za-z0-9_./-]+\.(?:json|xml|png|jpg|jpeg|wotmod|pyc|py|bnk|log)\b')


def catalog(path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    result = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('TEXT', 'PANEL'):
                    result[target.id] = ast.literal_eval(node.value)
    if set(result) != {'TEXT', 'PANEL'}:
        raise ValueError('Missing TEXT or PANEL catalog: ' + str(path))
    return result


def leaves(value, prefix=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, prefix + (key,))
    else:
        yield prefix, value


def validate_catalogs(root=ROOT):
    folder = root / 'mod/res/scripts/client/Driftkings/i18n'
    manifest = json.loads((root / 'build_data/locales.json').read_text(encoding='utf-8'))
    reference = dict(leaves(catalog(folder / 'en.py')))
    errors = []
    for code in manifest['locales']:
        actual = dict(leaves(catalog(folder / (code + '.py'))))
        for key in sorted(set(reference) - set(actual)):
            errors.append('%s: missing %s' % (code, '.'.join(key)))
        for key in sorted(set(actual) - set(reference)):
            errors.append('%s: unexpected %s' % (code, '.'.join(key)))
        for key in set(reference) & set(actual):
            source, translated = reference[key], actual[key]
            if not isinstance(translated, type(source)):
                errors.append('%s: wrong value type at %s' % (code, '.'.join(key)))
            elif isinstance(source, str):
                if source.strip() and not translated.strip():
                    errors.append('%s: empty translation at %s' % (code, '.'.join(key)))
                if Counter(FORMATTING.findall(source)) != Counter(FORMATTING.findall(translated)):
                    errors.append('%s: changed formatting at %s' % (code, '.'.join(key)))
                if re.fullmatch(r'#[0-9A-Fa-f]{6,8}', source) and translated != source:
                    errors.append('%s: changed color at %s' % (code, '.'.join(key)))
                for path in set(PATHS.findall(source)):
                    if translated.count(path) != source.count(path):
                        errors.append('%s: changed resource path at %s: %s' % (code, '.'.join(key), path))
    if errors:
        raise ValueError('Locale validation failed:\n' + '\n'.join(errors[:60]))
    english = catalog(folder / 'en.py')
    return {'locales': len(manifest['locales']),
            'componentKeys': sum(len(section) for section in english['TEXT'].values()),
            'panelKeys': len(english['PANEL']), 'status': 'passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(validate_catalogs(args.root), indent=2))
