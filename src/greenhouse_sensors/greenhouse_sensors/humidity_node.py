#!/usr/bin/env python3
"""Publish simulated greenhouse relative humidity readings."""

from __future__ import annotations

from typing import List, Optional

from greenhouse_common.runtime import run_node
from greenhouse_sensors.sensor_node import ScalarSensorNode


class HumiditySensor(ScalarSensorNode):
    """Sensor node publishing relative humidity as a percentage."""

    def __init__(self) -> None:
        super().__init__(
            node_name='humidity_sensor',
            topic='humidity',
            unit='%',
            set_point=60.0,
            noise_stddev=5.0,
            minimum=0.0,
            maximum=100.0,
            publish_rate=1.0,
        )


def main(args: Optional[List[str]] = None) -> None:
    """Run the humidity sensor node."""
    run_node(HumiditySensor, args)


if __name__ == '__main__':
    main()
