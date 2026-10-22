# -*- coding: utf-8 -*-
"""Resolve native and name-mangled attributes without changing the target."""
_sentinel = object()


def find_attr_name(obj, name, accept_property=False):
    if not name.endswith('__'):
        while name.startswith('_'):
            name = name[1:]
    full_name = '__'.join((getattr(obj, '__name__', obj.__class__.__name__), name))
    if not full_name.startswith('_'):
        full_name = '_' + full_name
    suf_name = '_' + name
    for _name in ((full_name, suf_name, name), (name, suf_name, full_name))[accept_property]:
        if hasattr(obj, _name):
            return _name


def find_attr(obj, name, default=_sentinel, accept_property=False):
    _name = find_attr_name(obj, name, accept_property)
    return default if _name is None and default is not _sentinel else getattr(obj, _name or '_' + name)

