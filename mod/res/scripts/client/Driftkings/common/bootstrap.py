# -*- coding: utf-8 -*-
def _read(namespace, name):
    if name not in namespace:
        raise NameError("global name '%s' is not defined" % name)
    return namespace[name]


def initializeCore(namespace):
    try:
        _read(namespace, 'logStartupInfo')()
        _read(namespace, 'initializeSubsystems')()
        return True
    except Exception as e:
        _read(namespace, 'logError')(_read(namespace, '__CORE_NAME__'), 'Failed to initialize core: {0}', e)
        if getattr(_read(namespace, 'sys'), 'DEBUG', False):
            _read(namespace, 'logError')(_read(namespace, '__CORE_NAME__'), 'Traceback: {0}', ''.join(_read(namespace, 'traceback').format_exception(*_read(namespace, 'sys').exc_info())))
        return False

def logStartupInfo(namespace):
    separator = '=' * 70
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), separator)
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), '================[Loading and Started]=================================')
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), '================[v.{}]==============================', _read(namespace, 'VERSION'))
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), separator)
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), 'Initialization time: {0}', _read(namespace, 'time').strftime('%Y-%m-%d %H:%M:%S'))
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), 'Current client version: {0}', _read(namespace, 'curCV'))
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), separator)

def initializeSubsystems(namespace):
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), 'Initializing subsystems...')
    _read(namespace, 'logInfo')(_read(namespace, '__CORE_NAME__'), 'Subsystems initialized successfully')
