# Copyright 2026 Imad Elghadaoui
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pure monitoring helpers for the greenhouse alert system."""

from __future__ import annotations

from typing import Optional


def is_critical(value: float, threshold: float, *, above: bool = True) -> bool:
    """Return True when ``value`` has crossed the critical ``threshold``."""
    return value >= threshold if above else value <= threshold


class AlertCooldown:
    """
    Rate-limit alerts so a persistent condition does not spam subscribers.

    The clock is injected through :meth:`should_alert` instead of being read
    internally, which keeps the class free of ROS dependencies and easy to
    test with explicit timestamps.
    """

    def __init__(self, cooldown_seconds: float) -> None:
        if cooldown_seconds < 0.0:
            raise ValueError('cooldown_seconds must be non-negative')
        self._cooldown = float(cooldown_seconds)
        self._last_alert: Optional[float] = None

    @property
    def cooldown_seconds(self) -> float:
        """Return the configured cooldown in seconds."""
        return self._cooldown

    def should_alert(self, now: float) -> bool:
        """Return True when an alert may be raised at time ``now``."""
        if self._last_alert is None or (now - self._last_alert) >= self._cooldown:
            self._last_alert = now
            return True
        return False

    def reset(self) -> None:
        """Forget the last alert time."""
        self._last_alert = None
