"""Sensor simulation model used by the greenhouse sensor nodes."""

from __future__ import annotations

import random
from typing import Optional


class GaussianSensorModel:
    """
    Generate plausible readings around a configurable set point.

    Readings follow a Gaussian distribution centred on ``set_point`` and are
    clamped to the sensor's physical range. Passing ``seed`` makes the
    sequence reproducible, which the tests rely on.
    """

    def __init__(
        self,
        set_point: float,
        noise_stddev: float,
        minimum: float,
        maximum: float,
        seed: Optional[int] = None,
    ) -> None:
        if minimum >= maximum:
            raise ValueError('minimum must be strictly smaller than maximum')
        if noise_stddev < 0.0:
            raise ValueError('noise_stddev must be non-negative')
        if not minimum <= set_point <= maximum:
            raise ValueError('set_point must lie within [minimum, maximum]')
        self._set_point = float(set_point)
        self._noise_stddev = float(noise_stddev)
        self._minimum = float(minimum)
        self._maximum = float(maximum)
        self._random = random.Random(seed)

    @property
    def minimum(self) -> float:
        """Return the lower bound of the sensor range."""
        return self._minimum

    @property
    def maximum(self) -> float:
        """Return the upper bound of the sensor range."""
        return self._maximum

    def read(self) -> float:
        """Return a single simulated reading clamped to the sensor range."""
        value = self._random.gauss(self._set_point, self._noise_stddev)
        return min(max(value, self._minimum), self._maximum)
