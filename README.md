# Guía de instalación y ejecución — MARTHA

Esta guía explica cómo preparar el entorno de desarrollo y ejecutar la simulación de **MARTHA** con ROS 2 Humble. Incluye las soluciones a problemas de compilación encontrados durante la puesta en marcha.

> **Alcance:** procedimiento de instalación y lanzamiento. La carga correcta del brazo EB300, la garra y sus controladores debe validarse por separado en Gazebo y ROS 2.

## 1. Requisitos previos

- Ubuntu 22.04 LTS.
- ROS 2 Humble instalado.
- Herramientas `git`, `colcon` y `rosdep` disponibles.
- Dependencias de simulación requeridas por el repositorio (Gazebo y paquetes ROS 2 asociados).

Comprobar que ROS 2 está disponible:

```bash
source /opt/ros/humble/setup.bash
ros2 pkg list
```

> `ros2 pkg list` permite comprobar que la CLI de ROS 2 está disponible.

## 2. Preparar el workspace

En una instalación nueva, crea el workspace convencional:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

Clona **una sola vez** el repositorio dentro de `src`:

```bash
git clone https://github.com/Embedar/martha_nav_robotic_arm.git
```

La estructura esperada es:

```text
~/ros2_ws/
├── src/
│   └── martha_nav_robotic_arm/
├── build/      # Se crea al compilar
├── install/    # Se crea al compilar
└── log/        # Se crea al compilar
```

> Si ya tienes el repositorio en `~/ros2_ws/src/martha_nav_robotic_arm`, **no vuelvas a clonarlo**. Actualízalo mediante `git pull` solamente cuando quieras incorporar cambios remotos y hayas revisado tus modificaciones locales.

## 3. Resolver dependencias y compilar

Desde la raíz del workspace:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws

# Instalar dependencias declaradas por los paquetes (requiere rosdep configurado)
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble

# Compilar
colcon build --symlink-install
```

Al finalizar, carga los paquetes de tu workspace:

```bash
source ~/ros2_ws/install/setup.bash
```

Verifica que ROS 2 reconoce el paquete:

```bash
ros2 pkg prefix martha_nav
```

> Si `rosdep` indica que falta un paquete o una clave de dependencia, revisa el mensaje de error antes de continuar. No todas las dependencias específicas de la simulación necesariamente están declaradas en el repositorio.

## 4. Ejecutar la simulación

En una terminal con el entorno cargado:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 launch martha_nav sim.launch.py \
  robot:=martha_tower \
  drive:=mecanum \
  with_arm:=true
```

Los argumentos usados en este proyecto son:

| Argumento | Valor utilizado | Finalidad |
|---|---|---|
| `robot` | `martha_tower` | Seleccionar la variante de MARTHA con torre. |
| `drive` | `mecanum` | Seleccionar el modelo de tracción mecanum. |
| `with_arm` | `true` | Solicitar la inclusión del brazo en la simulación. |

Para consultar los argumentos realmente admitidos por tu versión del archivo de lanzamiento:

```bash
ros2 launch martha_nav sim.launch.py --show-args
```

**Importante:** que el launch se ejecute no demuestra por sí solo que el brazo, la garra ni `ros2_control` estén operativos; comprueba su presencia y sus interfaces.

## 5. Comandos rápidos para sesiones posteriores

Si el proyecto ya fue compilado y no cambiaste archivos que requieren nueva instalación o compilación:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch martha_nav sim.launch.py \
  robot:=martha_tower \
  drive:=mecanum \
  with_arm:=true
```

Si modificaste código o archivos instalados por el paquete:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 6. Verificaciones básicas

En una **segunda terminal**, carga primero ROS 2 y el workspace:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 node list
ros2 topic list
ros2 action list
```

Si los controladores de `ros2_control` están presentes, inspecciónalos con:

```bash
ros2 control list_controllers
```

> Este último comando requiere que la interfaz de `controller_manager` correspondiente esté activa. Si no aparece, revisa la configuración de control del robot antes de asumir que los controladores funcionan.

## 7. Solución de problemas frecuentes

### A. `Duplicate package names not supported`

**Causa:** `colcon` encontró más de una copia de un paquete con el mismo nombre. Por ejemplo:

```text
~/ros2_ws/martha_nav_robotic_arm/martha_nav_robotic_arm/
~/ros2_ws/src/martha_nav_robotic_arm/
```

**Solución:** conserva una única copia activa dentro de `src`. Antes de mover nada, verifica las rutas:

```bash
cd ~/ros2_ws
find . -name package.xml -not -path './build/*' -not -path './install/*'
```

Si confirmas que la carpeta adicional es una copia duplicada y no contiene trabajo que necesites en este workspace, puedes apartarla sin borrarla:

```bash
mv ~/ros2_ws/martha_nav_robotic_arm ~/martha_nav_robotic_arm_backup
```

Este comando corresponde **solamente** al caso donde existe esa carpeta adicional. No lo ejecutes si no existe o si allí está tu única copia de trabajo.

### B. `Package 'martha_nav' not found`

**Causa probable:** no cargaste el entorno generado por `colcon`, o el paquete no se instaló correctamente.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 pkg prefix martha_nav
```

Si aún no aparece, vuelve a compilar desde `~/ros2_ws` y revisa el resultado.

### C. `can't copy .../build/martha_nav/launch/burger.launch.py`

Este error apareció tras reorganizar un workspace con paquetes duplicados. Puede deberse a artefactos de compilación anteriores o a un problema de instalación del paquete.

Primero limpia **solo los artefactos del paquete afectado**:

```bash
cd ~/ros2_ws
rm -rf build/martha_nav install/martha_nav
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select martha_nav
source install/setup.bash
```

Si el error persiste, comprueba que el archivo fuente existe y que la configuración de instalación lo referencia correctamente:

```bash
find ~/ros2_ws/src/martha_nav_robotic_arm -name 'burger.launch.py'
find ~/ros2_ws/src/martha_nav_robotic_arm -name 'setup.py'
```

No borres todo el workspace ni modifiques `setup.py` sin identificar primero la causa.

## 8. Buenas prácticas

- Ejecuta `colcon build` desde la **raíz del workspace** (`~/ros2_ws`), no desde `src`.
- Mantén una única copia activa de cada paquete ROS 2.
- Tras compilar, ejecuta `source install/setup.bash` en la terminal donde vas a lanzar ROS 2.
- Cuando abras una terminal nueva, vuelve a cargar los entornos.
- Usa `--show-args` para confirmar las opciones de cada launch.
- Valida por separado descripción URDF/Xacro, simulación física, articulaciones, controladores y garra.

---

**Entorno de referencia:** Ubuntu 22.04 LTS · ROS 2 Humble · MARTHA · Gazebo.
