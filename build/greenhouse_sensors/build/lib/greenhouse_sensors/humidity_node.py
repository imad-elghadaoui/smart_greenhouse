import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class HumiditySensor(Node):
    def __init__(self):
        super().__init__('humidity_sensor')
        self.publisher = self.create_publisher(Float32, 'humidity', 10)
        self.timer = self.create_timer(1.0, self.publish_humidity)

    def publish_humidity(self):
        msg = Float32()
        msg.data = 60.0 + random.uniform(-5.0, 5.0)  # Simulate humidity
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing humidity: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = HumiditySensor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
