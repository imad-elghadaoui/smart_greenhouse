"""Tests for greenhouse_common.validation."""

import math

import pytest

from greenhouse_common.validation import is_valid_reading


@pytest.mark.parametrize('value', [0.0, 20.0, 100.0])
def test_accepts_values_inside_range(value):
    assert is_valid_reading(value, 0.0, 100.0)


@pytest.mark.parametrize('value', [-0.1, 100.1])
def test_rejects_values_outside_range(value):
    assert not is_valid_reading(value, 0.0, 100.0)


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_rejects_non_finite_values(value):
    assert not is_valid_reading(value, -1000.0, 1000.0)


def test_includes_both_bounds():
    assert is_valid_reading(0.0, 0.0, 100.0)
    assert is_valid_reading(100.0, 0.0, 100.0)
