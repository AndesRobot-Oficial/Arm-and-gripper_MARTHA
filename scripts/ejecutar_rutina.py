#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration

from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from action_msgs.msg import GoalStatus


class RutinaBrazo(Node):

    def __init__(self):
        super().__init__('ejecutar_rutina')

        self.joints = [f'joint_{i}' for i in range(1, 7)]
        self.posicion_actual = None

        # Parámetros configurables
        self.declare_parameter('amplitud', 0.03)
        self.declare_parameter('tiempo_paso', 1.5)

        self.suscripcion = self.create_subscription(
            JointState,
            '/joint_states',
            self.recibir_estado,
            10
        )

        self.cliente = ActionClient(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )

    def recibir_estado(self, msg):
        posiciones = dict(zip(msg.name, msg.position))

        if all(j in posiciones for j in self.joints):
            self.posicion_actual = [
                posiciones[j] for j in self.joints
            ]

    def enviar_trayectoria(self, inicial, amplitud, tiempo):

        # Desplazamientos relativos a la posición inicial
        movimientos = [
            [1.0, -1.0, 0.7, -0.7, 0.6, -0.5],
            [-1.0, 1.0, -0.7, 0.7, -0.6, 0.5],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ]

        objetivo = FollowJointTrajectory.Goal()
        objetivo.trajectory.joint_names = self.joints

        for i, desplazamientos in enumerate(movimientos):

            punto = JointTrajectoryPoint()

            punto.positions = [
                inicial[j] + amplitud * desplazamientos[j]
                for j in range(6)
            ]

            punto.velocities = [0.0] * 6

            punto.time_from_start = Duration(
                seconds=(i + 1) * tiempo
            ).to_msg()

            objetivo.trajectory.points.append(punto)

        futuro = self.cliente.send_goal_async(objetivo)
        rclpy.spin_until_future_complete(self, futuro)

        handle = futuro.result()

        if handle is None or not handle.accepted:
            self.get_logger().error('Trayectoria rechazada')
            return False

        resultado_futuro = handle.get_result_async()
        rclpy.spin_until_future_complete(
            self, resultado_futuro
        )

        respuesta = resultado_futuro.result()

        if respuesta is None:
            return False

        return (
            respuesta.status == GoalStatus.STATUS_SUCCEEDED
            and respuesta.result.error_code == 0
        )

    def ejecutar(self):

        amplitud = float(
            self.get_parameter('amplitud').value
        )

        tiempo = float(
            self.get_parameter('tiempo_paso').value
        )

        if not 0.0 < amplitud <= 0.05 or tiempo < 1.0:
            self.get_logger().error(
                'Parámetros fuera del rango de prueba'
            )
            return

        self.get_logger().info('Esperando articulaciones...')

        limite = time.monotonic() + 10.0

        while rclpy.ok() and self.posicion_actual is None:
            rclpy.spin_once(self, timeout_sec=0.2)

            if time.monotonic() > limite:
                self.get_logger().error('Sin estado articular')
                return

        if not self.cliente.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Controlador no disponible')
            return

        # Referencia fija para evitar desplazamiento acumulativo
        inicial = self.posicion_actual.copy()

        ciclo = 0

        self.get_logger().info('Iniciando rutina continua')

        while rclpy.ok():

            ciclo += 1
            self.get_logger().info(f'Ciclo {ciclo}')

            exito = self.enviar_trayectoria(
                inicial, amplitud, tiempo
            )

            if not exito:
                self.get_logger().error(
                    'Rutina detenida por fallo'
                )
                break


def main(args=None):

    rclpy.init(args=args)
    nodo = RutinaBrazo()

    try:
        nodo.ejecutar()

    except KeyboardInterrupt:
        nodo.get_logger().info('Deteniendo rutina')

    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
