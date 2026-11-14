#!/usr/bin/env python3
"""Raise alerts and force ventilation when temperature becomes critical."""

from __future__ import annotations

from typing import List, Optional

from example_interfaces.srv import SetBool
from rclpy.client import Client
from rclpy.node import Node
from rclpy.task import Future
from std_msgs.msg import Float32

from greenhouse_common.runtime import run_node
from greenhouse_common.validation import is_valid_reading
from greenhouse_monitor.monitoring_logic import AlertCooldown, is_critical


class AlertSystem(Node):
    """Watch the temperature topic and request ventilation on critical readings."""

    def __init__(self) -> None:
        super().__init__('alert_system')
        self.declare_parameter('critical_temperature', 30.0)
        self.declare_parameter('alert_cooldown', 10.0)
        self.declare_parameter('min_valid_temperature', -40.0)
        self.declare_parameter('max_valid_temperature', 85.0)

        self._critical_temperature = self.get_parameter('critical_temperature').value
        self._min_valid = self.get_parameter('min_valid_temperature').value
        self._max_valid = self.get_parameter('max_valid_temperature').value
        self._cooldown = AlertCooldown(self.get_parameter('alert_cooldown').value)

        self._client: Client = self.create_client(SetBool, 'toggle_ventilation')
        self._subscription = self.create_subscription(
            Float32, 'temperature', self._on_temperature, 10)
        self.get_logger().info(
            f'Alert system ready (critical temperature {self._critical_temperature:.1f} degC)')

    def _on_temperature(self, message: Float32) -> None:
        if not is_valid_reading(message.data, self._min_valid, self._max_valid):
            self.get_logger().warning(
                f'Ignoring invalid temperature reading: {message.data!r}',
                throttle_duration_sec=5.0,
            )
            return
        if not is_critical(message.data, self._critical_temperature):
            return
        if not self._cooldown.should_alert(self.get_clock().now().nanoseconds / 1e9):
            return
        self.get_logger().warning(f'Critical temperature: {message.data:.1f} degC')
        self._request_ventilation()

    def _request_ventilation(self) -> None:
        if not self._client.service_is_ready():
            self.get_logger().error(
                'Ventilation service is not available', throttle_duration_sec=10.0)
            return
        request = SetBool.Request()
        request.data = True
        future = self._client.call_async(request)
        future.add_done_callback(self._on_response)

    def _on_response(self, future: Future) -> None:
        try:
            response = future.result()
        except Exception as exc:  # noqa: BLE001 - report any service failure
            self.get_logger().error(f'Ventilation service call failed: {exc!r}')
            return
        if response is None:
            self.get_logger().error('Ventilation service returned no response')
            return
        self.get_logger().info(f'Ventilation service response: {response.message}')


def main(args: Optional[List[str]] = None) -> None:
    """Run the alert system node."""
    run_node(AlertSystem, args)


if __name__ == '__main__':
    main()
