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

"""Control greenhouse irrigation from the humidity topic."""

from __future__ import annotations

from typing import List, Optional

from example_interfaces.srv import SetBool
from rclpy.node import Node
from std_msgs.msg import Bool, Float32

from greenhouse_common.qos import state_qos_profile
from greenhouse_common.runtime import run_node
from greenhouse_common.validation import is_valid_reading
from greenhouse_control.control_logic import HysteresisSwitch


class IrrigationController(Node):
    """Start irrigation when humidity drops and stop it when it recovers."""

    def __init__(self) -> None:
        super().__init__('irrigation_controller')
        self.declare_parameter('lower_humidity', 40.0)
        self.declare_parameter('upper_humidity', 60.0)
        self.declare_parameter('min_valid_humidity', 0.0)
        self.declare_parameter('max_valid_humidity', 100.0)
        self.declare_parameter('state_publish_rate', 1.0)

        self._min_valid = self.get_parameter('min_valid_humidity').value
        self._max_valid = self.get_parameter('max_valid_humidity').value
        self._switch = HysteresisSwitch(
            lower_threshold=self.get_parameter('lower_humidity').value,
            upper_threshold=self.get_parameter('upper_humidity').value,
            activate_above=False,
        )
        self._state_publisher = self.create_publisher(
            Bool, 'irrigation_state', state_qos_profile())
        self._subscription = self.create_subscription(
            Float32, 'humidity', self._on_humidity, 10)
        self._service = self.create_service(
            SetBool, 'toggle_irrigation', self._on_toggle)

        rate = float(self.get_parameter('state_publish_rate').value)
        if rate > 0.0:
            self._state_timer = self.create_timer(1.0 / rate, self._publish_state)
        else:
            self._state_timer = None

        self._publish_state()
        self.get_logger().info(
            'Irrigation controller ready '
            f'(on below {self._switch.lower_threshold:.1f} %, '
            f'off above {self._switch.upper_threshold:.1f} %)'
        )

    @property
    def is_active(self) -> bool:
        """Return True while irrigation is running."""
        return self._switch.state

    def _on_humidity(self, message: Float32) -> None:
        if not is_valid_reading(message.data, self._min_valid, self._max_valid):
            self.get_logger().warning(
                f'Ignoring invalid humidity reading: {message.data!r}',
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
                f'Humidity {message.data:.1f} % below threshold, irrigation on')
        else:
            self.get_logger().info(
                f'Humidity {message.data:.1f} % above threshold, irrigation off')

    def _on_toggle(self, request: SetBool.Request, response: SetBool.Response) -> SetBool.Response:
        self._switch.set_state(bool(request.data))
        self._publish_state()
        response.success = True
        response.message = 'Irrigation activated' if request.data else 'Irrigation deactivated'
        self.get_logger().info(f'Manual override: {response.message}')
        return response

    def _publish_state(self) -> None:
        message = Bool()
        message.data = self._switch.state
        self._state_publisher.publish(message)


def main(args: Optional[List[str]] = None) -> None:
    """Run the irrigation controller node."""
    run_node(IrrigationController, args)


if __name__ == '__main__':
    main()
