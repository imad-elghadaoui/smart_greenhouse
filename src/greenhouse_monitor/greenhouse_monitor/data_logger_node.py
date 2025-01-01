#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DataLogger(Node):
    def __init__(self):
        super().__init__('data_logger')
        self.temp_subscription = self.create_subscription(
            Float32,
            'temperature',
            self.temperature_callback,
            10)
        self.humid_subscription = self.create_subscription(
            Float32,
            'humidity',
            self.humidity_callback,
            10)
        self.get_logger().info("DataLogger node started.")

    def temperature_callback(self, msg):
        """Logs temperature data."""
        self.get_logger().info(f'Logging temperature: {msg.data}')

    def humidity_callback(self, msg):
        """Logs humidity data."""
        self.get_logger().info(f'Logging humidity: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = DataLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down DataLogger node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
