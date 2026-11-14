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
import launch_testing.asserts
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
                self._spin_until(lambda: len(received) > 0, timeout=10.0),
                f'{topic} did not deliver a retained value to a late subscriber')
            return received[-1]
        finally:
            self.node.destroy_subscription(subscription)

    def test_sensor_topics_stream(self):
        """Verify that sensor nodes actively stream plausible readings."""
        temperature_samples = []
        humidity_samples = []

        sub_temp = self.node.create_subscription(
            Float32,
            '/temperature',
            lambda msg: temperature_samples.append(msg.data),
            10,
        )
        sub_hum = self.node.create_subscription(
            Float32,
            '/humidity',
            lambda msg: humidity_samples.append(msg.data),
            10,
        )
        try:
            received_both = self._spin_until(
                lambda: bool(temperature_samples and humidity_samples),
                timeout=30.0,
            )
            self.assertTrue(received_both, 'Sensor topics did not stream within timeout')
            # Verify readings match physical bounds declared in configuration
            self.assertTrue(-40.0 <= temperature_samples[-1] <= 85.0)
            self.assertTrue(0.0 <= humidity_samples[-1] <= 100.0)
        finally:
            self.node.destroy_subscription(sub_temp)
            self.node.destroy_subscription(sub_hum)

    def test_state_topics_retain_last_value(self):
        """Verify that state topics retain their state for late subscribers."""
        for topic in ('/ventilation_state', '/irrigation_state'):
            with self.subTest(topic=topic):
                self.assertIn(self._retained_state(topic), (True, False))

    def test_toggle_ventilation_updates_state(self):
        """Verify that manual toggle service drives ventilation actuator state."""
        self._assert_toggle_drives_state('/toggle_ventilation', '/ventilation_state')

    def test_toggle_irrigation_updates_state(self):
        """Verify that manual toggle service drives irrigation actuator state."""
        self._assert_toggle_drives_state('/toggle_irrigation', '/irrigation_state')

    def _assert_toggle_drives_state(self, service, topic):
        received = []
        subscription = self.node.create_subscription(
            Bool, topic, lambda message: received.append(bool(message.data)), _state_qos())
        client = None
        try:
            client = self.node.create_client(SetBool, service)
            self.assertTrue(client.wait_for_service(timeout_sec=15.0),
                            f'{service} service is not available')

            # Activate actuator
            request = SetBool.Request()
            request.data = True
            future = client.call_async(request)
            self.assertTrue(self._spin_until(lambda: future.done(), timeout=15.0),
                            f'{service} service did not answer')
            self.assertTrue(future.result().success, f'{service} reported a failure')
            self.assertTrue(self._spin_until(lambda: True in received, timeout=10.0),
                            f'{topic} never reported an active actuator')

            # Cleanly deactivate actuator back to False
            request.data = False
            future_reset = client.call_async(request)
            self.assertTrue(self._spin_until(lambda: future_reset.done(), timeout=15.0),
                            f'{service} reset did not answer')
            self.assertTrue(future_reset.result().success, f'{service} reset reported a failure')
        finally:
            if client is not None:
                self.node.destroy_client(client)
            self.node.destroy_subscription(subscription)


@launch_testing.post_shutdown_test()
class TestGreenhouseShutdown(unittest.TestCase):
    """Verify that all greenhouse stack processes shut down cleanly."""

    def test_exit_codes(self, proc_info):
        """Assert all launched processes exited cleanly with code 0."""
        launch_testing.asserts.assertExitCodes(proc_info)
