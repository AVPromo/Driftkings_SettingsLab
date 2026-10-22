# -*- coding: utf-8 -*-
"""Finite float conversion shared by calculations and presentation."""
import math


def finite_number(value, default=None):
    """Convert to float, preserving the caller's fallback for invalid input."""
    try:
        value = float(value)
        return default if math.isnan(value) or math.isinf(value) else value
    except (ValueError, TypeError, OverflowError):
        return default
