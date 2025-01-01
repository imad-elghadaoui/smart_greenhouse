#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from example_interfaces.srv import SetBool

class AlertSystem(Node):
    def __init__(self):
        super().__init__('alert_system')
        self.client = self.create_client(SetBool, 'toggle_ventilation')
        self.temp_subscription = self.create_subscription(
            Float32,
            'temperature',
            self.temperature_callback,
            10)
        self.get_logger().info("AlertSystem node started.")

    def temperature_callback(self, msg):
        """Handles critical temperature alerts."""
        if msg.data > 30.0:
            self.send_alert(f'Critical temperature: {msg.data}°C')
            self.activate_ventilation()

    def send_alert(self, message):
        """Sends an alert message."""
        self.get_logger().warn(message)

    def activate_ventilation(self):
        """Sends a request to activate ventilation."""
        if not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Ventilation service not available!")
            return

        request = SetBool.Request()
        request.data = True
        future = self.client.call_async(request)
        future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        """Handles the response from the ventilation service."""
        try:
            response = future.result()
            self.get_logger().info(f"Ventilation response: {response.message}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = AlertSystem()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down AlertSystem node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
