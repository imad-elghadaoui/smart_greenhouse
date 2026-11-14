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

"""Tests for greenhouse_control.control_logic."""

import pytest

from greenhouse_control.control_logic import HysteresisSwitch


def test_activates_above_upper_threshold():
    switch = HysteresisSwitch(20.0, 25.0)
    assert switch.update(26.0) is True
    assert switch.state is True


def test_deactivates_below_lower_threshold():
    switch = HysteresisSwitch(20.0, 25.0, initial_state=True)
    assert switch.update(19.0) is False


def test_keeps_state_between_thresholds():
    switch = HysteresisSwitch(20.0, 25.0)
    assert switch.update(22.0) is False
    switch.update(26.0)
    assert switch.update(22.0) is True


def test_threshold_boundaries_are_inclusive():
    switch = HysteresisSwitch(20.0, 25.0)
    assert switch.update(25.0) is True
    assert switch.update(20.0) is False


def test_triggers_on_low_values_when_activate_above_is_false():
    switch = HysteresisSwitch(40.0, 60.0, activate_above=False)
    assert switch.update(39.0) is True
    assert switch.update(50.0) is True
    assert switch.update(61.0) is False


def test_manual_override_sets_state():
    switch = HysteresisSwitch(20.0, 25.0)
    switch.set_state(True)
    assert switch.state is True


def test_rejects_inverted_thresholds():
    with pytest.raises(ValueError):
        HysteresisSwitch(25.0, 20.0)
