# -*- coding: utf-8 -*-
"""Persisted hotkey conversion, with no engine initialization at import time."""

__all__ = ('processHotKeys',)

KEY_ALT, KEY_CONTROL, KEY_SHIFT = range(-1, -4, -1)
SPECIAL_TO_KEYS = {
    KEY_ALT: ['KEY_LALT', 'KEY_RALT'],
    KEY_CONTROL: ['KEY_LCONTROL', 'KEY_RCONTROL'],
    KEY_SHIFT: ['KEY_LSHIFT', 'KEY_RSHIFT']}


def _native_key_name(key):
    # Preserve the client's naming policy; load it only for a code needing it.
    import BigWorld
    return BigWorld.keyToString(key)


def processHotKeys(data, keys, mode):
    add = lambda key: key if 'KEY_' in key else 'KEY_' + key
    if mode == 'read':
        import Keys
        process = lambda key: getattr(Keys, add(key))
    elif mode == 'write':
        process = lambda key: SPECIAL_TO_KEYS.get(key) or add(_native_key_name(key))
    else:
        assert False, 'unknown hotkey conversion mode'
    make = lambda keySet: [make(key) if isinstance(key, (list, tuple)) else process(key) for key in keySet]
    for dataKey in keys:
        newKey = dataKey.replace('key', 'Key')
        if (newKey if mode == 'read' else dataKey) not in data:
            continue
        data[(dataKey if mode == 'read' else newKey)] = make(data.pop((newKey if mode == 'read' else dataKey)))
