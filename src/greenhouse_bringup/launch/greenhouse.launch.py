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
