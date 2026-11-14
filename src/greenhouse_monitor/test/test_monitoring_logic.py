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

"""Tests for greenhouse_monitor.monitoring_logic."""

from greenhouse_monitor.monitoring_logic import AlertCooldown, is_critical
import pytest


def test_is_critical_above_threshold():
    assert is_critical(30.0, 30.0)
    assert is_critical(31.0, 30.0)
    assert not is_critical(29.9, 30.0)


def test_is_critical_below_threshold():
    assert is_critical(4.0, 5.0, above=False)
    assert not is_critical(6.0, 5.0, above=False)


def test_cooldown_allows_first_alert_then_blocks():
    cooldown = AlertCooldown(10.0)
    assert cooldown.should_alert(0.0)
    assert not cooldown.should_alert(5.0)
    assert cooldown.should_alert(10.0)


def test_cooldown_reset_allows_immediate_alert():
    cooldown = AlertCooldown(10.0)
    cooldown.should_alert(0.0)
    cooldown.reset()
    assert cooldown.should_alert(1.0)


def test_zero_cooldown_always_alerts():
    cooldown = AlertCooldown(0.0)
    assert cooldown.should_alert(0.0)
    assert cooldown.should_alert(0.0)


def test_rejects_negative_cooldown():
    with pytest.raises(ValueError):
        AlertCooldown(-1.0)
