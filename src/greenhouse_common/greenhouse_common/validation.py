"""Validation helpers shared by the greenhouse nodes."""

from __future__ import annotations

import math


def is_valid_reading(value: float, minimum: float, maximum: float) -> bool:
    """
    Return True when ``value`` is finite and within the closed range.

    Sensor drivers can return NaN, infinity or out-of-range values when a
    device is missing or misconfigured. Rejecting those readings before they
    reach the control logic keeps the actuators in a safe state.
    """
    return math.isfinite(value) and minimum <= value <= maximum
