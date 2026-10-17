# -*- coding: utf-8 -*-
"""Explicit composition, dependency gating and reverse-order cleanup."""
import importlib
import logging
LOG = logging.getLogger('Driftkings.Loader')


class ServiceSpec(object):
    def __init__(self, name, factory, requires=(), phase='foundation'):
        self.name, self.factory = name, factory
        self.requires, self.phase = tuple(requires), phase


def runtime_service(path, construct=True):
    def create():
        module, attribute = path.split(':')
        value = getattr(importlib.import_module(module), attribute)
        return value() if construct else value
    return create


class CommonRuntime(object):
    def start(self):
        importlib.import_module('Driftkings.common')

    def stop(self):
        pass


def default_services():
    # Factories contain paths only; no engine modules or services are created here.
    return (
        ServiceSpec('common', CommonRuntime),
        ServiceSpec('settings', runtime_service('Driftkings.settings.runtime:SettingsRuntime'), ('common',)),
        ServiceSpec('dossiers', runtime_service('Driftkings.common.utils.achievement_dossiers:DossierService'), ('common',)),
        ServiceSpec('lifecycle', runtime_service('Driftkings.core.lifecycle:lifecycle', False), ('common',)),
        ServiceSpec('keyboard', runtime_service('Driftkings.core.keyboard:keyboard', False), ('lifecycle',)),
        ServiceSpec('battle_events', runtime_service('Driftkings.core.battle_events:battleEvents', False), ('keyboard', 'lifecycle')),
        ServiceSpec('callbacks', runtime_service('Driftkings.core.callbacks:callbacks', False), ('battle_events',)),
        ServiceSpec('notifications', runtime_service('Driftkings.core.notifications:NotificationsService'), ('callbacks',)),
        ServiceSpec('window_views', runtime_service('Driftkings.views.hangar.windows:WindowViews'), ('settings', 'callbacks'), 'interface'),
        ServiceSpec('battle_views', runtime_service('Driftkings.views:BattleViews'), ('settings', 'battle_events', 'callbacks'), 'interface'),
        ServiceSpec('settings_panel', runtime_service('Driftkings.settings:SettingsService'), ('settings', 'keyboard', 'window_views'), 'interface'),
        ServiceSpec('updater', runtime_service('Driftkings.core.updater:UpdaterService'), ('settings_panel', 'callbacks'), 'interface'),
    )


class Core(object):
    def __init__(self, names=None, importer=None, services=None, hook_manager=None, context_factory=None):
        self.names = tuple(names) if names is not None else None
        self.importer = importer or importlib.import_module
        self.runtime = services is None
        self.specs = default_services() if self.runtime else tuple(
            service if isinstance(service, ServiceSpec) else ServiceSpec(service.__class__.__name__, lambda value=service: value, phase='interface')
            for service in services)
        self.hooks = hook_manager
        self.context_factory = context_factory
        self.contexts = None
        self.modules, self.initialized, self.services = [], [], []
        self.service_state, self.instances = {}, {}
        self.disabled, self.failures, self.cleaned = {}, [], set()
        self.started = self.closed = False

    def _owner(self, name):
        return 'Driftkings.' + name

    def _activate(self, owner):
        if self.hooks is not None:
            self.hooks.current = owner
            self.hooks.activate(owner)

    def _release(self):
        if self.hooks is not None:
            self.hooks.current = None

    def _deactivate(self, owner):
        if self.hooks is not None:
            self.hooks.deactivate(owner)

    def _startServices(self, phase):
        for spec in self.specs:
            if spec.phase != phase:
                continue
            missing = [name for name in spec.requires if self.service_state.get(name) != 'active']
            if missing:
                self.service_state[spec.name] = 'blocked'
                self.disabled['service:' + spec.name] = 'Unavailable dependencies: ' + ', '.join(missing)
                continue
            owner, service = self._owner('service.' + spec.name), None
            try:
                self._activate(owner)
                service = spec.factory()
                if hasattr(service, 'registerModule'):
                    for name, module in self.modules:
                        service.registerModule(module)
                if hasattr(service, 'register'):
                    for name, module in self.modules:
                        for definition in getattr(module, 'getBattleViews', lambda: ())():
                            service.register(*definition)
                service.start()
                self.services.append(service)
                self.instances[spec.name] = service
                self.service_state[spec.name] = 'active'
            except Exception:
                self.service_state[spec.name] = 'failed'
                self.failures.append('service:' + spec.name)
                LOG.exception('Could not start service %s', spec.name)
                self._deactivate(owner)
                if service is not None:
                    try:
                        service.stop()
                    except Exception:
                        LOG.exception('Partial service cleanup failed: %s', spec.name)
            finally:
                self._release()

    def _requirements(self, name, module=None):
        required = set(getattr(module, 'REQUIRES_SERVICES', ()))
        if self.runtime:
            required.update(('common', 'settings', 'lifecycle', 'keyboard', 'callbacks', 'battle_events'))
            if name in ('battle.battle_marks_of_excellence', 'lobby.hangar_marks_of_excellence'):
                required.add('dossiers')
            if module is not None:
                if getattr(module, 'getBattleViews', None):
                    required.add('battle_views')
                if getattr(module, 'getWindowViews', None):
                    required.add('window_views')
        return sorted(required)

    def _missing(self, name, module=None):
        return [key for key in self._requirements(name, module) if self.service_state.get(key) != 'active']

    def start(self):
        if self.started or self.closed:
            return
        self.started = True
        if self.hooks is None and self.runtime:
            from Driftkings.core.hooks import hooks
            self.hooks = hooks
        if self.names is None:
            from Driftkings.component_list import COMPONENTS
            self.names = tuple(COMPONENTS)
        self._startServices('foundation')
        for name in self.names:
            missing = self._missing(name)
            if missing:
                self.disabled[name] = 'Unavailable dependencies: ' + ', '.join(missing)
                continue
            try:
                # Import declares hooks; activation happens after service registration.
                if self.hooks is not None:
                    self.hooks.current = self._owner(name)
                module = self.importer(self._owner(name))
                self.modules.append((name, module))
            except Exception:
                self.failures.append(name)
                LOG.exception('Could not import component %s', name)
                self._deactivate(self._owner(name))
                if self.hooks is not None:
                    self.hooks.discard(self._owner(name))
                self._disableSettings(name)
            finally:
                self._release()
        self._startServices('interface')
        for name, module in self.modules:
            missing = self._missing(name, module)
            if missing:
                self.disabled[name] = 'Unavailable dependencies: ' + ', '.join(missing)
                self._stopComponent(name, module)
                self._disableSettings(name)
                continue
            try:
                self._activate(self._owner(name))
                callback = getattr(module, 'init', None)
                if callback is not None:
                    callback()
                self.initialized.append((name, module))
            except Exception:
                self.failures.append(name)
                LOG.exception('Could not initialize component %s', name)
                self._stopComponent(name, module)
                self._disableSettings(name)
            finally:
                self._release()
        if self.context_factory is None and self.runtime:
            from Driftkings.core.contexts import Contexts
            self.context_factory = Contexts
        if self.context_factory is not None:
            try:
                owners = self.initialized + [('service:' + name, service) for name, service in self.instances.items()
                                             if hasattr(service, 'onContextEntered')]
                self.contexts = self.context_factory(owners)
                self.contexts.start()
            except Exception:
                self.failures.append('Contexts')
                LOG.exception('Could not start Core contexts')
                if self.contexts is not None:
                    try:
                        self.contexts.stop()
                    except Exception:
                        LOG.exception('Partial context cleanup failed')
                    self.contexts = None
        self._summary()

    def _disableSettings(self, name):
        settings = self.instances.get('settings')
        disable = getattr(settings, 'disableOwner', None)
        if callable(disable):
            disable(self._owner(name))

    def _summary(self):
        metadata = {}
        if self.runtime:
            from Driftkings import VERSION
            metadata['mod'] = VERSION
            try:
                from helpers import getClientVersion
                from realm import CURRENT_REALM
                metadata.update(game=getClientVersion(), realm=CURRENT_REALM)
            except Exception:
                LOG.warning('Client startup metadata unavailable', exc_info=True)
        message = 'Startup complete: metadata=%s components=%s services=%s failures=%s disabled=%s' % (
            metadata, [name for name, module in self.initialized], self.service_state, self.failures, self.disabled)
        if self.runtime:
            try:
                import BigWorld
                BigWorld.logInfo('Driftkings.Loader', message, None)
                return
            except Exception:
                LOG.warning('Native startup log unavailable', exc_info=True)
        LOG.info(message)

    def stop(self):
        if self.closed:
            return
        self.closed = True
        if self.contexts is not None:
            try:
                self.contexts.stop()
            except Exception:
                LOG.exception('Could not stop Core contexts')
            self.contexts = None
        for name, module in reversed(self.modules):
            self._stopComponent(name, module)
        for spec in reversed(self.specs):
            service = self.instances.get(spec.name)
            if service is None:
                continue
            self._deactivate(self._owner('service.' + spec.name))
            try:
                service.stop()
            except Exception:
                LOG.exception('Could not stop service %s', spec.name)
            self.service_state[spec.name] = 'stopped'
        self.modules, self.services = [], []
        self.instances.clear()
        self.started = False
        self._release()

    def _stopComponent(self, name, module):
        if name in self.cleaned:
            return
        self.cleaned.add(name)
        self._deactivate(self._owner(name))
        try:
            callback = getattr(module, 'fini', None)
            if callback is not None:
                callback()
        except Exception:
            LOG.exception('Could not shut down component %s', name)
        finally:
            callbacks = self.instances.get('callbacks')
            try:
                if callbacks is not None:
                    callbacks.cancelOwner(self._owner(name))
            except Exception:
                LOG.exception('Could not cancel component callbacks: %s', name)
            finally:
                self._deactivate(self._owner(name))
