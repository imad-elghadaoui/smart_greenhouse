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

"""Tests for greenhouse_sensors.sensor_model."""

import pytest

from greenhouse_sensors.sensor_model import GaussianSensorModel


def test_seeded_model_is_reproducible():
    first = GaussianSensorModel(20.0, 2.0, -40.0, 85.0, seed=42)
    second = GaussianSensorModel(20.0, 2.0, -40.0, 85.0, seed=42)
    assert [first.read() for _ in range(10)] == [second.read() for _ in range(10)]


def test_readings_stay_within_range():
    model = GaussianSensorModel(0.0, 100.0, -5.0, 5.0, seed=1)
    assert all(-5.0 <= model.read() <= 5.0 for _ in range(1000))


def test_model_exposes_its_bounds():
    model = GaussianSensorModel(0.0, 1.0, -5.0, 5.0)
    assert model.minimum == -5.0
    assert model.maximum == 5.0


@pytest.mark.parametrize(
    'arguments',
    [
        (20.0, 1.0, 10.0, 10.0),
        (20.0, 1.0, 30.0, 10.0),
        (20.0, -1.0, 0.0, 30.0),
        (50.0, 1.0, 0.0, 30.0),
    ],
)
def test_rejects_invalid_configuration(arguments):
    with pytest.raises(ValueError):
        GaussianSensorModel(*arguments)
