"""Pure control logic for the greenhouse actuators."""

from __future__ import annotations


class HysteresisSwitch:
    """
    Two-threshold switch that prevents actuator chatter.

    The switch turns on when the measurement crosses ``upper_threshold`` and
    turns off when it crosses ``lower_threshold``. Between the two thresholds
    the previous state is kept, which avoids rapid toggling around a single
    set point. Set ``activate_above=False`` for actuators that must turn on
    when the measurement falls, such as irrigation on low humidity.
    """

    def __init__(
        self,
        lower_threshold: float,
        upper_threshold: float,
        *,
        activate_above: bool = True,
        initial_state: bool = False,
    ) -> None:
        if lower_threshold >= upper_threshold:
            raise ValueError('lower_threshold must be smaller than upper_threshold')
        self._lower = float(lower_threshold)
        self._upper = float(upper_threshold)
        self._activate_above = activate_above
        self._state = initial_state

    @property
    def lower_threshold(self) -> float:
        """Return the threshold below which the switch turns off."""
        return self._lower

    @property
    def upper_threshold(self) -> float:
        """Return the threshold above which the switch turns on."""
        return self._upper

    @property
    def state(self) -> bool:
        """Return the current actuator state."""
        return self._state

    def update(self, value: float) -> bool:
        """Feed a measurement and return the resulting actuator state."""
        if self._activate_above:
            if self._state and value <= self._lower:
                self._state = False
            elif not self._state and value >= self._upper:
                self._state = True
        else:
            if self._state and value >= self._upper:
                self._state = False
            elif not self._state and value <= self._lower:
                self._state = True
        return self._state

    def set_state(self, state: bool) -> None:
        """Force the actuator state, for example after a manual request."""
        self._state = bool(state)
