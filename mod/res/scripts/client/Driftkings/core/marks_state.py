# -*- coding: utf-8 -*-
"""Context-separated snapshots; game adapters own acquisition and lifecycle."""
import copy

from Driftkings.core.signals import Signal


class MarksState(object):
    def __init__(self):
        self.changed = Signal()
        self.values = {}

    def publish(self, context, payload):
        if self.values.get(context) == payload:
            return False
        self.values[context] = copy.deepcopy(payload)
        self.changed.emit(context)
        return True

    def snapshot(self, context):
        return copy.deepcopy(self.values.get(context, {'state': 'unavailable', 'vehicleId': None}))

    def clear(self, context):
        self.publish(context, {'state': 'unavailable', 'vehicleId': None})


marks_state = MarksState()
