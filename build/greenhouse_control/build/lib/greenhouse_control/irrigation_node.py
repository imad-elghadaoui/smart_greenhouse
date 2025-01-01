#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class IrrigationController(Node):
    def __init__(self):
        super().__init__('irrigation_controller')
        self.timer = self.create_timer(2.0, self.irrigation_cycle)
        self.irrigation_active = False
        self.get_logger().info("IrrigationController node started.")

    def irrigation_cycle(self):
        """Simulates an irrigation cycle."""
        if self.irrigation_active:
            self.get_logger().info("Irrigation in progress...")
        else:
            self.get_logger().info("Irrigation is currently off.")

def main(args=None):
    rclpy.init(args=args)
    node = IrrigationController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down IrrigationController node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
