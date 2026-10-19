"""Embed SVG artwork in the ES5 library without a runtime XML parser."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG', 'player', 'destroyed')
TARGET = ROOT / 'mod/res/gui/gameface/mods/Driftkings/TacticalMinimap/graphics.js'
START, END = '    // BEGIN GENERATED TACTICAL ICONS', '    // END GENERATED TACTICAL ICONS'
TAGS = {'defs', 'linearGradient', 'stop', 'path', 'g', 'rect', 'circle'}
ATTRS = {'id', 'x1', 'y1', 'x2', 'y2', 'offset', 'stop-color', 'd', 'fill', 'stroke',
         'stroke-width', 'stroke-linejoin', 'stroke-linecap', 'stroke-dasharray', 'opacity',
         'transform', 'x', 'y', 'width', 'height', 'rx', 'cx', 'cy', 'r'}


def element(node):
    tag = node.tag.rsplit('}', 1)[-1]
    if tag not in TAGS or set(node.attrib) - ATTRS:
        raise ValueError('Unsupported SVG element/attribute: ' + tag)
    for key, value in node.attrib.items():
        if len(value) > 2048 or '<' in value or '>' in value or '://' in value:
            raise ValueError('Invalid SVG attribute: ' + key)
        if 'url(' in value and value != 'url(#steel)':
            raise ValueError('Only the local steel gradient is allowed')
    return [tag, dict(node.attrib), [element(child) for child in node]]


def generated():
    icons = {}
    for kind in KINDS:
        data = (ROOT / 'prototypes/tactical_minimap/icons' / (kind + '.svg')).read_bytes()
        if len(data) > 20000:
            raise ValueError('SVG exceeds size limit: ' + kind)
        svg = ET.fromstring(data)
        if svg.attrib.get('viewBox') != '0 0 64 64':
            raise ValueError('Expected 64 x 64 viewBox: ' + kind)
        icons[kind] = {'viewBox': svg.attrib['viewBox'], 'sha256': hashlib.sha256(data).hexdigest(),
                       'nodes': [element(child) for child in svg]}
    return START + '\n    var icons = ' + json.dumps(icons, ensure_ascii=True, sort_keys=True) + ';\n' + END


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source = TARGET.read_text(encoding='utf-8')
    updated, count = re.subn(re.escape(START) + r'.*?' + re.escape(END), lambda match: generated(),
                             source, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Generated icon block missing')
    if args.write:
        TARGET.write_text(updated, encoding='utf-8')
    elif source != updated:
        parser.exit(1, 'Tactical icons are out of sync; run generate_tactical_icons.py --write\n')
    print('Tactical SVG definitions are in sync')


if __name__ == '__main__':
    main()
