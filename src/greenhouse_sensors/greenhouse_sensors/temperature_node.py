#!/usr/bin/env python3
"""Publish simulated greenhouse temperature readings."""

from __future__ import annotations

from typing import List, Optional

from greenhouse_common.runtime import run_node
from greenhouse_sensors.sensor_node import ScalarSensorNode


class TemperatureSensor(ScalarSensorNode):
    """Sensor node publishing temperature in degrees Celsius."""

    def __init__(self) -> None:
        super().__init__(
            node_name='temperature_sensor',
            topic='temperature',
            unit='degC',
            set_point=20.0,
            noise_stddev=2.0,
            minimum=-40.0,
            maximum=85.0,
            publish_rate=1.0,
        )


def main(args: Optional[List[str]] = None) -> None:
    """Run the temperature sensor node."""
    run_node(TemperatureSensor, args)


if __name__ == '__main__':
    main()
