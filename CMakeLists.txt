cmake_minimum_required(VERSION 3.8)
project(martha_arm)

find_package(ament_cmake REQUIRED)

# Instalar archivos necesarios para la simulacion
install(
  DIRECTORY
    scripts
    config
    launch
    meshes
    rviz
    urdf
  DESTINATION share/${PROJECT_NAME}
)

# Instalar ejecutable de rutinas del brazo
install(
  PROGRAMS
    scripts/ejecutar_rutina.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME ejecutar_rutina
)

ament_package()
