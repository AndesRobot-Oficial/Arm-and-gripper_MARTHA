"""MARTHA + ascensor + EB300 + pinza en Gazebo Classic (ROS 2 Humble).

Lanzamiento deliberadamente fijo y minimo para el proyecto de manipulacion.
Uso: ros2 launch martha_nav sim.launch.py

- MARTHA con mecanum y torre corta, siempre.
- Ascensor, brazo y pinza, siempre.
- Gazebo con mundo vacio (suelo y gravedad) y GUI.
- Un controller_manager creado por el plugin gazebo_ros2_control del URDF.
- Sin SLAM, EKF, planificadores, politica de navegacion ni robot alternativo.
"""

from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


CONTROLLERS = (
    "joint_state_broadcaster",
    "mecanum_drive_controller",
    "lift_controller",
    "arm_controller",
    "gripper_controller",
)


def _controller_spawner(name):
    """Activa un controlador del controller_manager ya creado por Gazebo."""
    return Node(
        package="controller_manager",
        executable="spawner",
        name=f"spawn_{name}",
        output="screen",
        arguments=[
            name,
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120",
        ],
    )


def _start_next_on_success(process, next_action, label):
    """Evita activar controladores si falla el spawn o el anterior."""
    def on_exit(event, context):
        if event.returncode != 0:
            return [LogInfo(msg=f"[ERROR] {label} fallo (codigo {event.returncode}). Revisa la consola.")]
        return [next_action]

    return RegisterEventHandler(
        OnProcessExit(target_action=process, on_exit=on_exit)
    )


def generate_launch_description():
    share = Path(get_package_share_directory("martha_nav"))
    model_file = share / "urdf" / "martha.urdf.xacro"
    controllers_file = share / "config" / "controllers.yaml"

    for file in (model_file, controllers_file):
        if not file.is_file():
            raise FileNotFoundError(f"Archivo de simulacion no instalado: {file}")

    # Procesar una sola vez. Si hay un error Xacro, falla antes de abrir Gazebo.
    xml = xacro.process_file(
        str(model_file),
        mappings={
            "drive": "mecanum",
            "tower": "true",
            "with_arm": "true",
            "controllers_file": str(controllers_file),
            "lidar_visualize": "false",
        },
    ).toxml()

    gazebo_server = ExecuteProcess(
        cmd=[
            "gzserver", "--verbose",
            "-s", "libgazebo_ros_init.so",
            "-s", "libgazebo_ros_factory.so",
        ],
        output="screen",
    )

    gazebo_gui = ExecuteProcess(
        cmd=["gzclient"],
        output="screen",
    )

    state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": ParameterValue(xml, value_type=str),
            "use_sim_time": True,
        }],
    )

    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_martha",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-entity", "martha",
            "-x", "0.0", "-y", "0.0", "-z", "0.03",
            "-timeout", "180",
        ],
    )

    spawners = [_controller_spawner(name) for name in CONTROLLERS]

    # El controller_manager aparece cuando Gazebo inserta el robot.
    # No usar TimerAction ni iniciar todos los controladores a la vez.
    sequence = [
        _start_next_on_success(spawn_robot, spawners[0], "Spawn de MARTHA")
    ]
    sequence += [
        _start_next_on_success(current, following, CONTROLLERS[index])
        for index, (current, following) in enumerate(zip(spawners, spawners[1:]))
    ]

    return LaunchDescription([
        gazebo_server,
        gazebo_gui,
        state_publisher,
        spawn_robot,
        *sequence,
    ])