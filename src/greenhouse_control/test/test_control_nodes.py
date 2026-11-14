"""Behaviour tests for the ventilation and irrigation nodes (require rclpy)."""

import math

import pytest

rclpy = pytest.importorskip('rclpy')

from std_msgs.msg import Float32  # noqa: E402

from greenhouse_control.irrigation_node import IrrigationController  # noqa: E402
from greenhouse_control.ventilation_node import VentilationController  # noqa: E402


@pytest.fixture(scope='module', autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_ventilation_reacts_to_temperature():
    node = VentilationController()
    try:
        assert node.is_active is False
        node._on_temperature(Float32(data=26.0))
        assert node.is_active is True
        node._on_temperature(Float32(data=19.0))
        assert node.is_active is False
    finally:
        node.destroy_node()


def test_ventilation_ignores_invalid_reading():
    node = VentilationController()
    try:
        node._on_temperature(Float32(data=math.nan))
        assert node.is_active is False
    finally:
        node.destroy_node()


def test_irrigation_starts_on_low_humidity():
    node = IrrigationController()
    try:
        node._on_humidity(Float32(data=35.0))
        assert node.is_active is True
        node._on_humidity(Float32(data=65.0))
        assert node.is_active is False
    finally:
        node.destroy_node()
