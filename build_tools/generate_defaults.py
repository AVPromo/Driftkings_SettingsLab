"""Generate Python 2.7 fallback values from the distribution JSON defaults."""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import pprint

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'mod/res/scripts/client/Driftkings/settings/default_values.py'
PROFILES = ('none', 'short', 'medium', 'medium2', 'large')


def read_object(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key in %s: %s' % (path, key))
            result[key] = value
        return result
    value = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                       parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON value: ' + value)))
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object: ' + str(path))
    def finite(item):
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError('Nonfinite JSON number: ' + str(path))
        if isinstance(item, dict):
            for child in item.values(): finite(child)
        elif isinstance(item, list):
            for child in item: finite(child)
    finite(value)
    return value


def assemble(root=ROOT):
    config = read_object(root / 'build_data/build_config.json')
    source = root / config['defaults']['source_root']
    section_source = ast.parse((root / 'mod/res/scripts/client/Driftkings/settings/sections.py').read_text(encoding='utf-8'))
    section_names = next(ast.literal_eval(node.value) for node in section_source.body if isinstance(node, ast.Assign)
                         and any(isinstance(target, ast.Name) and target.id == 'COMPONENT_NAMES' for target in node.targets))
    constants = ast.parse((root / 'mod/res/scripts/client/Driftkings/_constants.py').read_text(encoding='utf-8'))
    declared_names = set()
    for node in constants.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == 'NAME':
                            declared_names.add(ast.literal_eval(item.value))
                        elif isinstance(target, ast.Name) and target.id == 'ID':
                            raise ValueError('Configuration classes must use NAME only: ' + node.name)
    documents = {}
    def document(name):
        if name not in documents:
            documents[name] = read_object(source / name)
        return documents[name]
    defaults = {}
    for path in sorted((root / config['components']['directory']).glob('*.json')):
        manifest = read_object(path)
        if manifest['kind'] != 'feature':
            continue
        identifier = manifest['id']
        if section_names[identifier] not in declared_names:
            raise ValueError('Unknown canonical configuration section: ' + identifier)
        declared = set(manifest['config_files'])
        if not declared:
            # Features may share another section instead of owning a settings page.
            continue
        def get(name):
            if name not in declared:
                raise ValueError('%s does not declare default %s' % (identifier, name))
            return document(name)
        if identifier == 'TeamPanels':
            prefix = 'default/team_panels/'
            data = dict(get(prefix + 'general.json'))
            data.update(get(prefix + 'playersPanel.json'))
            data['loading'] = dict(get(prefix + 'battleLoading.json'))
            data['loading'].pop('tips', None)  # Retired native loading option.
            data['tab'] = get(prefix + 'statisticForm.json')
            data['profiles'] = {name: get(prefix + 'panel' + name.title() + '.json') for name in PROFILES}
        elif identifier == 'VehicleCarousel':
            prefix = 'default/vehicle_carousel/'
            general = get(prefix + 'carousel.json')
            data = {key: general[key] for key in ('enabled', 'showIcons', 'colorRating')}
            data['carousel'] = {key: value for key, value in general.items() if key not in data}
            data['carousel'].update(normal=get(prefix + 'carouselNormal.json'), small=get(prefix + 'carouselSmall.json'))
        elif identifier == 'MinimapEnhancements':
            data = {}
            for name in ('minimap.json', 'minimap_labels.json', 'minimap_circles.json', 'minimap_lines.json'):
                part = get('default/minimap_enhancements/' + name)
                overlap = set(part) & set(data)
                if overlap:
                    raise ValueError('Duplicate minimap sections: ' + ', '.join(sorted(overlap)))
                data.update(part)
        else:
            if len(declared) != 1:
                raise ValueError('Expected one defaults document for ' + identifier)
            data = get(next(iter(declared)))
        defaults[section_names[identifier]] = data
    selector = document('load.json')
    if not isinstance(selector.get('loadConfig'), str) or not selector['loadConfig']:
        raise ValueError('Missing default configuration profile')
    return defaults, selector, documents


def render(root=ROOT):
    defaults, selector, documents = assemble(root)
    hashes = {name: hashlib.sha256(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
              for name, value in sorted(documents.items())}
    # ASCII literals plus unicode_literals work identically on Python 2.7 and 3.
    literal = lambda value: pprint.pformat(json.loads(json.dumps(value)), width=110, sort_dicts=True).encode('ascii', 'backslashreplace').decode('ascii')
    return ('# -*- coding: utf-8 -*-\n'
            '"""Generated from res/configs/Driftkings. Edit the JSON, never this file.\n\n'
            'Regenerate: python build_tools/generate_defaults.py --write\n'
            '"""\nfrom __future__ import unicode_literals\n\n'
            'SOURCE_HASHES = ' + literal(hashes) + '\n\n'
            'SELECTOR = ' + literal(selector) + '\n\n'
            'DEFAULTS = ' + literal(defaults) + '\n')


def check_generated(root=ROOT):
    path = root / TARGET
    if not path.is_file() or path.read_text(encoding='utf-8') != render(root):
        raise ValueError('Python defaults differ from JSON. Run python build_tools/generate_defaults.py --write')


def refresh_snapshot(root=ROOT):
    path = root / 'build_data/defaults_snapshot.json'
    snapshot = read_object(path)
    config = read_object(root / 'build_data/build_config.json')
    source = root / config['defaults']['source_root']
    for item in snapshot['files']:
        item['sha256'] = hashlib.sha256((source / item['path']).read_bytes()).hexdigest()
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate the checked-in Python fallback')
    parser.add_argument('--refresh-snapshot', action='store_true', help='Record intentional edits to the JSON defaults')
    args = parser.parse_args()
    if args.refresh_snapshot and not args.write:
        parser.error('--refresh-snapshot requires --write')
    if args.write:
        (ROOT / TARGET).write_text(render(ROOT), encoding='utf-8')
        if args.refresh_snapshot:
            refresh_snapshot(ROOT)
    check_generated(ROOT)
    print('Defaults match the canonical JSON: %d components' % len(assemble(ROOT)[0]))
