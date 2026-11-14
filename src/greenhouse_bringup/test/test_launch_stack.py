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

"""End-to-end launch test: start the whole stack and probe its interfaces."""

import os
import time
import unittest

import launch
import launch_testing
import launch_testing.actions
import launch_testing_ros
import pytest
import rclpy
from ament_index_python.packages import get_package_share_directory
from example_interfaces.srv import SetBool
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from rclpy.node import Node
from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)
from std_msgs.msg import Bool, Float32


@pytest.mark.launch_test
def generate_test_description():
    """Launch the full greenhouse stack and wait until it is ready."""
    launch_file = os.path.join(
        get_package_share_directory('greenhouse_bringup'),
        'launch',
        'greenhouse.launch.py',
    )
    return launch.LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file),
        ),
        launch_testing.actions.ReadyToTest(),
    ]), {'launch_file': launch_file}


def _state_qos() -> QoSProfile:
    """Return the transient-local QoS the state topics are published with."""
    return QoSProfile(
        depth=1,
        history=QoSHistoryPolicy.KEEP_LAST,
        reliability=QoSReliabilityPolicy.RELIABLE,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    )


class TestGreenhouseStack(unittest.TestCase):
    """Check that the launched stack exposes the documented interfaces."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = Node('greenhouse_integration_probe')

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def _spin_until(self, predicate, timeout=20.0):
        """Spin the probe node until ``predicate`` is True or the timeout hits."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if predicate():
                return True
        return predicate()

    def _retained_state(self, topic):
        """Return the retained value of a transient-local state topic."""
        received = []
        subscription = self.node.create_subscription(
            Bool, topic, lambda message: received.append(bool(message.data)), _state_qos())
        try:
            self.assertTrue(
                self._spin_until(lambda: received, timeout=10.0),
                f'{topic} did not deliver a retained value to a late subscriber')
            return received[-1]
        finally:
            self.node.destroy_subscription(subscription)

    def test_sensor_topics_stream(self):
        topics = [('/temperature', Float32), ('/humidity', Float32)]
        with launch_testing_ros.WaitForTopics(topics, timeout=30.0) as wait_for_topics:
            self.assertEqual(wait_for_topics.topics_not_received(), set())

    def test_state_topics_retain_last_value(self):
        for topic in ('/ventilation_state', '/irrigation_state'):
            with self.subTest(topic=topic):
                self.assertIn(self._retained_state(topic), (True, False))

    def test_toggle_ventilation_updates_state(self):
        self._assert_toggle_drives_state('/toggle_ventilation', '/ventilation_state')

    def test_toggle_irrigation_updates_state(self):
        self._assert_toggle_drives_state('/toggle_irrigation', '/irrigation_state')

    def _assert_toggle_drives_state(self, service, topic):
        received = []
        subscription = self.node.create_subscription(
            Bool, topic, lambda message: received.append(bool(message.data)), _state_qos())
        try:
            client = self.node.create_client(SetBool, service)
            self.assertTrue(client.wait_for_service(timeout_sec=15.0),
                            f'{service} service is not available')

            request = SetBool.Request()
            request.data = True
            future = client.call_async(request)
            self.assertTrue(self._spin_until(lambda: future.done(), timeout=15.0),
                            f'{service} service did not answer')
            self.assertTrue(future.result().success, f'{service} reported a failure')
            self.assertTrue(self._spin_until(lambda: True in received, timeout=10.0),
                            f'{topic} never reported an active actuator')
        finally:
            self.node.destroy_subscription(subscription)
