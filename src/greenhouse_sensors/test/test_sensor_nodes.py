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

"""Smoke tests for the greenhouse sensor nodes (require rclpy)."""

import pytest

rclpy = pytest.importorskip('rclpy')

from greenhouse_sensors.humidity_node import HumiditySensor  # noqa: E402
from greenhouse_sensors.temperature_node import TemperatureSensor  # noqa: E402


@pytest.fixture(scope='module', autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.mark.parametrize(
    ('node_type', 'node_name'),
    [(TemperatureSensor, 'temperature_sensor'), (HumiditySensor, 'humidity_sensor')],
)
def test_sensor_node_declares_expected_parameters(node_type, node_name):
    node = node_type()
    try:
        assert node.get_name() == node_name
        for parameter in ('publish_rate', 'set_point', 'noise_stddev', 'min_valid', 'max_valid'):
            assert node.has_parameter(parameter)
    finally:
        node.destroy_node()
