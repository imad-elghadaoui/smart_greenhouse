#!/usr/bin/env python3
"""Log greenhouse sensor readings to the console and optionally to a CSV file."""

from __future__ import annotations

import time
from typing import List, Optional

from rclpy.node import Node
from std_msgs.msg import Float32

from greenhouse_common.runtime import run_node
from greenhouse_monitor.csv_recorder import CsvRecorder


class DataLogger(Node):
    """Subscribe to the sensor topics and record every sample."""

    def __init__(self) -> None:
        super().__init__('data_logger')
        self.declare_parameter('log_directory', '')
        self.declare_parameter('log_filename', 'greenhouse_log.csv')

        self._recorder = self._create_recorder()
        self._temperature_subscription = self.create_subscription(
            Float32, 'temperature', self._on_temperature, 10)
        self._humidity_subscription = self.create_subscription(
            Float32, 'humidity', self._on_humidity, 10)

    def _create_recorder(self) -> Optional[CsvRecorder]:
        log_directory = self.get_parameter('log_directory').value
        if not log_directory:
            self.get_logger().info('Logging samples to the console only')
            return None
        filename = self.get_parameter('log_filename').value
        recorder = CsvRecorder(f'{log_directory.rstrip("/")}/{filename}')
        try:
            recorder.open()
        except OSError as exc:
            self.get_logger().error(f'Could not open log file {recorder.path}: {exc}')
            return None
        self.get_logger().info(f'Logging samples to {recorder.path}')
        return recorder

    def _on_temperature(self, message: Float32) -> None:
        self._record('temperature', message.data)

    def _on_humidity(self, message: Float32) -> None:
        self._record('humidity', message.data)

    def _record(self, topic: str, value: float) -> None:
        self.get_logger().info(f'{topic}: {value:.2f}')
        if self._recorder is None:
            return
        try:
            self._recorder.append(time.time(), topic, value)
        except OSError as exc:
            self.get_logger().error(
                f'Failed to write log entry: {exc}', throttle_duration_sec=10.0)

    def destroy_node(self) -> bool:
        if self._recorder is not None:
            self._recorder.close()
            self._recorder = None
        return super().destroy_node()


def main(args: Optional[List[str]] = None) -> None:
    """Run the data logger node."""
    run_node(DataLogger, args)


if __name__ == '__main__':
    main()
