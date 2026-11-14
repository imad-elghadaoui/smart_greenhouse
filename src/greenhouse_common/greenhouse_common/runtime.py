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

"""Helpers to start and stop rclpy nodes consistently."""

from __future__ import annotations

import sys
from typing import List, Optional, Type

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def run_node(node_type: Type[Node], args: Optional[List[str]] = None) -> None:
    """
    Create ``node_type``, spin it and shut it down cleanly.

    ``KeyboardInterrupt`` (Ctrl+C) and ``ExternalShutdownException`` (raised
    when another part of the process shuts rclpy down) are treated as normal
    termination. Any other exception is reported and turned into a non-zero
    exit code so that failures stay visible to process supervisors.
    """
    rclpy.init(args=args)
    node: Optional[Node] = None
    failed = False
    try:
        node = node_type()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception as exc:  # noqa: BLE001 - report any startup or runtime failure
        failed = True
        message = f'Node terminated unexpectedly: {exc!r}'
        if node is not None:
            node.get_logger().fatal(message)
        else:
            print(message, file=sys.stderr)
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if failed:
        sys.exit(1)
