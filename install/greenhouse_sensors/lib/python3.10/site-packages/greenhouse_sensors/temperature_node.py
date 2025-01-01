#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class TemperatureSensor(Node):
    def __init__(self):
        super().__init__('temperature_sensor')
        self.publisher = self.create_publisher(Float32, 'temperature', 10)
        self.timer = self.create_timer(1.0, self.publish_temperature)
        
    def publish_temperature(self):
        msg = Float32()
        msg.data = 20.0 + random.uniform(-2.0, 2.0)
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing temperature: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureSensor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
