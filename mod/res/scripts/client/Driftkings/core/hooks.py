# -*- coding: utf-8 -*-
"""Declare hooks during import; Core installs them and owns their lifetime."""
from functools import partial, wraps
from inspect import isclass
from Driftkings.core.diagnostics import diagnostics


class HookRegistry(object):
    def __init__(self):
        self.pending = {}
        self.active = set()
        self.current = None
        self.installations = {}
        self.subscriptions = {}

    def declare(self, owner, installer, handler, key=None):
        owner = self.current or owner
        token = (owner, key, handler)
        if token in self.installations:
            return handler
        valid = [True]
        metadata = handler
        while isinstance(metadata, partial):
            metadata = metadata.func
        metric = 'hook.' + str(owner) + '.' + getattr(metadata, '__name__', 'handler')
        if isinstance(key, tuple) and len(key) == 3:
            metric += ':' + getattr(key[0], '__name__', 'target') + '.' + str(key[1]) + '.' + str(key[2])
        @wraps(metadata)
        def guarded(original, *args, **kwargs):
            if valid[0] and owner in self.active:
                if diagnostics.enabled:
                    return diagnostics.call(metric, handler, original, *args, **kwargs)
                return handler(original, *args, **kwargs)
            # Classmethod hooks receive cls explicitly although original is bound.
            if args and isclass(getattr(original, '__self__', None)) and isclass(args[0]):
                return original(*args[1:], **kwargs)
            return original(*args, **kwargs)
        installed = [False]
        def operation():
            if not installed[0]:
                installer(guarded)
                installed[0] = True
        operation.valid = valid
        self.installations[token] = operation
        self.pending.setdefault(owner, []).append(operation)
        if owner in self.active:
            operation()
        return handler

    def activate(self, owner):
        if owner in self.active:
            return
        self.active.add(owner)
        try:
            for operation in self.pending.get(owner, ()):
                operation()
            for signal, callback in self.subscriptions.get(owner, ()):
                signal.connect(callback)
        except Exception:
            self.deactivate(owner)
            raise

    def deactivate(self, owner):
        # Leave wrappers in the chain, forwarding originals without mod behavior.
        self.active.discard(owner)
        for signal, callback in self.subscriptions.get(owner, ()):
            signal.disconnect(callback)

    def discard(self, owner):
        """Abandon declarations from an import that did not complete."""
        self.deactivate(owner)
        for token, operation in list(self.installations.items()):
            if token[0] == owner:
                operation.valid[0] = False
                del self.installations[token]
        self.pending.pop(owner, None)
        self.subscriptions.pop(owner, None)

    def subscribe(self, signal, handler):
        owner = self.current or getattr(handler, '__module__', None)
        entries = self.subscriptions.setdefault(owner, [])
        entry = (signal, handler)
        if entry not in entries:
            entries.append(entry)
            if owner in self.active:
                signal.connect(handler)
        return handler


hooks = HookRegistry()
_UNSET = object()


def override(obj, prop=_UNSET, getter=None, setter=None, deleter=None):
    if getter is None and setter is None and deleter is None:
        return lambda handler: override(obj, handler.__name__ if prop is _UNSET else prop, handler)
    from Driftkings.common.utils.monkeypatch import override as install
    if prop is _UNSET:
        prop = getter.__name__
    for kind, handler in (('getter', getter), ('setter', setter), ('deleter', deleter)):
        if handler is not None:
            installer = lambda guarded, kind=kind: install(obj, prop, **{kind: guarded})
            function = handler
            while isinstance(function, partial):
                function = function.func
            hooks.declare(getattr(function, '__module__', hooks.current), installer, handler, (obj, prop, kind))
    return getter


def _typed(kind, cls, method):
    def decorator(handler):
        def installer(guarded):
            from Driftkings.common.utils import monkeypatch
            getattr(monkeypatch, kind)(cls, method)(guarded)
        return hooks.declare(handler.__module__, installer, handler, (cls, method, kind))
    return decorator


def overrideMethod(cls, method):
    return _typed('overrideMethod', cls, method)


def overrideStaticMethod(cls, method):
    return _typed('overrideStaticMethod', cls, method)


def overrideClassMethod(cls, method):
    return _typed('overrideClassMethod', cls, method)


def on_event(signal, handler=None):
    """Declare an owner-bound subscription, connected only while its owner is active."""
    signal = getattr(signal, 'event', signal)
    if handler is None:
        return lambda callback: hooks.subscribe(signal, callback)
    return hooks.subscribe(signal, handler)
