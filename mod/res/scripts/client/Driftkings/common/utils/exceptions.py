# -*- coding: utf-8 -*-
"""Exception boundary for callbacks that must not propagate into the client."""
import logging
from functools import wraps


def log_exceptions(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            logging.getLogger(function.__module__).exception(
                'Callback failed: %s', function.__name__)
            return None
    return guarded
