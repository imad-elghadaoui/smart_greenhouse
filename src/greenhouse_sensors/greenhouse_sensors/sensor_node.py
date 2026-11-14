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

"""Base class shared by the greenhouse sensor nodes."""

from __future__ import annotations

from rclpy.node import Node
from std_msgs.msg import Float32

from greenhouse_common.validation import is_valid_reading
from greenhouse_sensors.sensor_model import GaussianSensorModel


class ScalarSensorNode(Node):
    """
    Publish a scalar sensor reading at a fixed rate.

    Concrete sensors only provide their name, topic, unit and default
    calibration. Sampling, validation, publication and logging live here so
    that every sensor behaves the same way and exposes the same parameters.
    """

    def __init__(
        self,
        node_name: str,
        topic: str,
        unit: str,
        *,
        set_point: float,
        noise_stddev: float,
        minimum: float,
        maximum: float,
        publish_rate: float,
    ) -> None:
        super().__init__(node_name)
        self._unit = unit
        self.declare_parameter('publish_rate', float(publish_rate))
        self.declare_parameter('set_point', float(set_point))
        self.declare_parameter('noise_stddev', float(noise_stddev))
        self.declare_parameter('min_valid', float(minimum))
        self.declare_parameter('max_valid', float(maximum))

        publish_rate = self.get_parameter('publish_rate').value
        minimum = self.get_parameter('min_valid').value
        maximum = self.get_parameter('max_valid').value
        if publish_rate <= 0.0:
            raise ValueError('publish_rate must be positive')

        self._minimum = minimum
        self._maximum = maximum
        self._model = GaussianSensorModel(
            set_point=self.get_parameter('set_point').value,
            noise_stddev=self.get_parameter('noise_stddev').value,
            minimum=minimum,
            maximum=maximum,
        )
        self._publisher = self.create_publisher(Float32, topic, 10)
        self._timer = self.create_timer(1.0 / publish_rate, self._publish)
        self.get_logger().info(
            f'Publishing {topic} at {publish_rate:.2f} Hz '
            f'[{unit}, valid range {minimum}..{maximum}]'
        )

    def _publish(self) -> None:
        value = self._model.read()
        if not is_valid_reading(value, self._minimum, self._maximum):
            self.get_logger().warning(
                f'Discarding out-of-range reading: {value!r}',
                throttle_duration_sec=5.0,
            )
            return
        message = Float32()
        message.data = value
        self._publisher.publish(message)
        self.get_logger().debug(f'{value:.2f} {self._unit}')
