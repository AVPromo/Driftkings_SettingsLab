# -*- coding: utf-8 -*-
"""Declarative control metadata, independent of storage and panel construction."""
import copy


def metadata(spec, **values):
    spec.update(values)
    return spec


def label(key, ctx='setting'):
    return {'type': 'Label', 'labelKey': key, 'labelContext': ctx}


def caption(text):
    return {'type': 'Label', 'text': text}


def control(key, kind='CheckBox', width=200, empty=False, button=None, value=None):
    item = {'type': kind, 'varName': key, 'width': width}
    if not empty:
        item['labelKey'] = key
    if button is not None:
        item['button'] = button
    return item


def options(key, choices, kind='Dropdown', width=200, empty=False, button=None, value=None):
    item = control(key, kind, width, empty, button, value)
    item['options'] = [{'label': choice} for choice in choices]
    return item


def images(key, icons, kind='Dropdown', width=200, empty=False, button=None, value=None):
    item = control(key, kind, width, empty, button, value)
    item.update(options=[{'label': name[:-4], 'image': 'gui/maps/icons/sixthsense/' + name} for name in icons], previewImage=True)
    return item


def hotkey(key, empty=False, value=None):
    return control(key, 'HotKey', empty=empty)


def slider(key, low, high, step, format_str='{{value}}', width=200, empty=False, button=None, value=None):
    if low > high or step <= 0:
        raise ValueError('Invalid slider limits: ' + key)
    item = control(key, 'Slider', width, empty, button, value)
    item.update(minimum=low, maximum=high, snapInterval=step, format=format_str)
    return item


def color(key, label_key):
    item = control(key, 'ColorChoice')
    item['colorLabelKey'] = label_key
    return item


def resolve(item, labels, values):
    """Resolve translations at panel-open time; declarations contain no live values."""
    item = copy.deepcopy(item)
    key = item.pop('labelKey', None)
    context = item.pop('labelContext', 'setting')
    if key is not None:
        prefix = 'UI_' + context + '_' + key
        item['text'] = labels[prefix + '_text']
        body = labels.get(prefix + '_tooltip', '')
        item['tooltip'] = '{HEADER}%s{/HEADER}{BODY}%s{/BODY}' % (item['text'], body) if body else ''
    color_key = item.pop('colorLabelKey', None)
    if color_key is not None:
        item['text'] = labels['UI_setting_' + color_key + '_text']
        tooltip = item.get('tooltip', '')
        if isinstance(tooltip, bytes):
            tooltip = tooltip.decode('utf-8')
        item['tooltip'] = tooltip % {item['varName']: values[item['varName']]}
    return item


def field(path, title, kind='CheckBox', low=None, high=None, choices=None,
          step=1, choice_labels=None, **metadata):
    """Define a nested setting without duplicating path/option conversions."""
    path = list(path)
    if not path:
        raise ValueError('Empty control path')
    item = {'varName': '.'.join(str(part) for part in path), 'path': path,
            'text': title, 'type': kind}
    if low is not None:
        if high is None or low > high or step <= 0:
            raise ValueError('Invalid slider limits: ' + item['varName'])
        item.update(minimum=low, maximum=high, snapInterval=step, canManualInput=True)
    if choices is not None:
        values = list(choices)
        labels = list(choice_labels) if choice_labels is not None else values
        if not values or len(values) != len(labels):
            raise ValueError('Invalid options: ' + item['varName'])
        item.update(options=[{'label': label} for label in labels], optionValues=values)
    item.update(metadata)
    return item
