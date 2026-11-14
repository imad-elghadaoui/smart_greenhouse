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

"""Reusable QoS profiles shared by the greenhouse nodes."""

from __future__ import annotations

from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)


def state_qos_profile() -> QoSProfile:
    """
    Return the QoS profile used for actuator state topics.

    Actuator state is a "last known value" signal: a reliable, transient-local,
    depth-1 profile keeps the most recent sample so that a subscriber which
    connects late (for example a monitoring tool started after the stack)
    immediately receives the current state instead of waiting for the next
    change.
    """
    return QoSProfile(
        depth=1,
        history=QoSHistoryPolicy.KEEP_LAST,
        reliability=QoSReliabilityPolicy.RELIABLE,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    )
