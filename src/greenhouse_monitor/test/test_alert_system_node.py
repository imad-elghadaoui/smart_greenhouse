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

"""Behaviour tests for the alert system node (require rclpy)."""

import pytest

rclpy = pytest.importorskip('rclpy')

from std_msgs.msg import Float32  # noqa: E402,I100

from greenhouse_monitor.alert_system_node import AlertSystem  # noqa: E402,I100


@pytest.fixture(scope='module', autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_uses_configured_critical_temperature():
    node = AlertSystem()
    try:
        assert node.get_parameter('critical_temperature').value == 30.0
    finally:
        node.destroy_node()


def test_critical_reading_without_service_does_not_raise():
    node = AlertSystem()
    try:
        node._on_temperature(Float32(data=35.0))
    finally:
        node.destroy_node()
