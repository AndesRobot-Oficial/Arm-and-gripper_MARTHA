import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from sensor_msgs.msg import JointState

rclpy.init()

node = Node(
    'martha_roller_visualizer',
    parameter_overrides=[
        Parameter('use_sim_time', value=True)
    ]
)

pub = node.create_publisher(
    JointState, '/joint_states', 10
)

ruedas = [
    'front_left',
    'front_right',
    'rear_left',
    'rear_right'
]

joints = [
    f'{rueda}_roller_{i:02d}_joint'
    for rueda in ruedas
    for i in range(12)
]

def publicar():
    msg = JointState()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.name = joints
    msg.position = [0.0] * len(joints)
    pub.publish(msg)

node.create_timer(0.1, publicar)

print("Publicando 48 rodillos para RViz")

try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.shutdown()