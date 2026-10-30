cmake_minimum_required(VERSION 3.8)
project(martha_arm)

find_package(ament_cmake REQUIRED)

# Instalar archivos necesarios para la simulacion
install(
  DIRECTORY
    config
    launch
    meshes
    rviz
    urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
