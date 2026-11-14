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

"""Tests for greenhouse_common.validation."""

import math

from greenhouse_common.validation import is_valid_reading
import pytest


@pytest.mark.parametrize('value', [0.0, 20.0, 100.0])
def test_accepts_values_inside_range(value):
    assert is_valid_reading(value, 0.0, 100.0)


@pytest.mark.parametrize('value', [-0.1, 100.1])
def test_rejects_values_outside_range(value):
    assert not is_valid_reading(value, 0.0, 100.0)


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_rejects_non_finite_values(value):
    assert not is_valid_reading(value, -1000.0, 1000.0)


def test_includes_both_bounds():
    assert is_valid_reading(0.0, 0.0, 100.0)
    assert is_valid_reading(100.0, 0.0, 100.0)
