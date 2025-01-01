#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from example_interfaces.srv import SetBool

class VentilationController(Node):
    def __init__(self):
        super().__init__('ventilation_controller')
        self.subscription = self.create_subscription(
            Float32,
            'temperature',
            self.temperature_callback,
            10)
        self.service = self.create_service(
            SetBool,
            'toggle_ventilation',
            self.toggle_ventilation_callback)
        self.ventilation_active = False
        self.get_logger().info("VentilationController node started.")

    def temperature_callback(self, msg):
        """Handles temperature updates and toggles ventilation if necessary."""
        if msg.data > 25.0 and not self.ventilation_active:
            self.ventilation_active = True
            self.get_logger().info('Temperature too high, activating ventilation.')
        elif msg.data < 20.0 and self.ventilation_active:
            self.ventilation_active = False
            self.get_logger().info('Temperature normal, deactivating ventilation.')

    def toggle_ventilation_callback(self, request, response):
        """Service callback to manually toggle ventilation."""
        self.ventilation_active = request.data
        response.success = True
        response.message = f'Ventilation {"activated" if request.data else "deactivated"}'
        self.get_logger().info(response.message)
        return response

def main(args=None):
    rclpy.init(args=args)
    node = VentilationController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down VentilationController node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
