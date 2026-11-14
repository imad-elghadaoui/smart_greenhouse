#!/usr/bin/env python3
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

"""Control greenhouse ventilation from the temperature topic."""

from __future__ import annotations

from typing import List, Optional

from example_interfaces.srv import SetBool
from rclpy.node import Node
from std_msgs.msg import Bool, Float32

from greenhouse_common.qos import state_qos_profile
from greenhouse_common.runtime import run_node
from greenhouse_common.validation import is_valid_reading
from greenhouse_control.control_logic import HysteresisSwitch


class VentilationController(Node):
    """Toggle ventilation on high temperature, with a manual override service."""

    def __init__(self) -> None:
        super().__init__('ventilation_controller')
        self.declare_parameter('lower_temperature', 20.0)
        self.declare_parameter('upper_temperature', 25.0)
        self.declare_parameter('min_valid_temperature', -40.0)
        self.declare_parameter('max_valid_temperature', 85.0)
        self.declare_parameter('state_publish_rate', 1.0)

        self._min_valid = self.get_parameter('min_valid_temperature').value
        self._max_valid = self.get_parameter('max_valid_temperature').value
        self._switch = HysteresisSwitch(
            lower_threshold=self.get_parameter('lower_temperature').value,
            upper_threshold=self.get_parameter('upper_temperature').value,
        )
        self._state_publisher = self.create_publisher(
            Bool, 'ventilation_state', state_qos_profile())
        self._subscription = self.create_subscription(
            Float32, 'temperature', self._on_temperature, 10)
        self._service = self.create_service(
            SetBool, 'toggle_ventilation', self._on_toggle)

        rate = float(self.get_parameter('state_publish_rate').value)
        if rate > 0.0:
            self._state_timer = self.create_timer(1.0 / rate, self._publish_state)
        else:
            self._state_timer = None

        self._publish_state()
        self.get_logger().info(
            'Ventilation controller ready '
            f'(on above {self._switch.upper_threshold:.1f} degC, '
            f'off below {self._switch.lower_threshold:.1f} degC)'
        )

    @property
    def is_active(self) -> bool:
        """Return True while ventilation is running."""
        return self._switch.state

    def _on_temperature(self, message: Float32) -> None:
        if not is_valid_reading(message.data, self._min_valid, self._max_valid):
            self.get_logger().warning(
                f'Ignoring invalid temperature reading: {message.data!r}',
                throttle_duration_sec=5.0,
            )
            return
        was_active = self._switch.state
        is_active = self._switch.update(float(message.data))
        if is_active == was_active:
            return
        self._publish_state()
        if is_active:
            self.get_logger().info(
                f'Temperature {message.data:.1f} degC above threshold, ventilation on')
        else:
            self.get_logger().info(
                f'Temperature {message.data:.1f} degC below threshold, ventilation off')

    def _on_toggle(self, request: SetBool.Request, response: SetBool.Response) -> SetBool.Response:
        self._switch.set_state(bool(request.data))
        self._publish_state()
        response.success = True
        response.message = 'Ventilation activated' if request.data else 'Ventilation deactivated'
        self.get_logger().info(f'Manual override: {response.message}')
        return response

    def _publish_state(self) -> None:
        message = Bool()
        message.data = self._switch.state
        self._state_publisher.publish(message)


def main(args: Optional[List[str]] = None) -> None:
    """Run the ventilation controller node."""
    run_node(VentilationController, args)


if __name__ == '__main__':
    main()
