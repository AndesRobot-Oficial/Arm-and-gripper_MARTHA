
cmake_minimum_required(VERSION 3.8)
project(martha_nav)

find_package(ament_cmake REQUIRED)

# Instalar los recursos del robot
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
