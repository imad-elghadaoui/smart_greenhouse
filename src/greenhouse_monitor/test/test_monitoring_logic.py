"""Tests for greenhouse_monitor.monitoring_logic."""

import pytest

from greenhouse_monitor.monitoring_logic import AlertCooldown, is_critical


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
