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

"""Launch the complete smart greenhouse stack with the default parameters."""

from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Return the launch description for the greenhouse stack."""
    parameters = PathJoinSubstitution(
        [FindPackageShare('greenhouse_bringup'), 'config', 'greenhouse_params.yaml'])

    nodes = [
        Node(
            package='greenhouse_sensors',
            executable='temperature_node',
            parameters=[parameters],
            output='screen',
        ),
        Node(
            package='greenhouse_sensors',
            executable='humidity_node',
            parameters=[parameters],
            output='screen',
        ),
        Node(
            package='greenhouse_control',
            executable='ventilation_node',
            parameters=[parameters],
            output='screen',
        ),
        Node(
            package='greenhouse_control',
            executable='irrigation_node',
            parameters=[parameters],
            output='screen',
        ),
        Node(
            package='greenhouse_monitor',
            executable='alert_system_node',
            parameters=[parameters],
            output='screen',
        ),
        Node(
            package='greenhouse_monitor',
            executable='data_logger_node',
            parameters=[parameters],
            output='screen',
        ),
    ]
    return LaunchDescription(nodes)
