
# RoboCup 2027 — Brazo Robótico y Garra de MARTHA

## 1. Descripción general

Proyecto de desarrollo e integración del sistema de manipulación robótica del robot móvil **MARTHA**, como parte de la preparación para **RoboCup 2027**.

El objetivo es adaptar el brazo robótico **EB300**, utilizado en el robot MILO, para incorporarlo a MARTHA junto con su garra, aprovechando los desarrollos existentes y manteniendo la compatibilidad con la arquitectura ROS 2 del equipo.

El desarrollo se concentra inicialmente en la simulación, el control de articulaciones y la integración de los componentes necesarios para realizar tareas de manipulación.

**Responsable:** Lorenzo Martínez Sandoval  
**Proyecto:** RoboCup 2027  
**Plataforma:** MARTHA  
**Brazo de referencia:** EB300 de MILO  
**Última actualización documental:** 2026-10-30  
**Último estado técnico registrado:** 2026-10-25

---

## 2. Objetivo principal

Integrar y validar en simulación el brazo robótico EB300 y su garra sobre la plataforma móvil MARTHA, reutilizando los componentes de MILO y garantizando una arquitectura modular compatible con ROS 2.

### Objetivos de desarrollo

1. Analizar la implementación existente del brazo y la garra de MILO.
2. Adaptar el modelo URDF/Xacro del brazo para MARTHA.
3. Integrar la estructura mecánica virtual, las articulaciones y sus límites.
4. Configurar y comprobar el control de articulaciones mediante ROS 2.
5. Implementar el control simulado de apertura y cierre de la garra.
6. Validar la integración con Gazebo y, cuando corresponda, MoveIt 2.
7. Preparar interfaces para futuras tareas autónomas de manipulación.

---

## 3. Estado actual

**Fase:** 0 — Reconocimiento, inventario y diagnóstico.

**Estado general:** Desarrollo inicial.

La decisión de reutilizar el brazo EB300 de MILO está aprobada. Se han identificado antecedentes de modelos URDF/Xacro y archivos de lanzamiento de MARTHA, pero todavía no se ha completado una auditoría del repositorio vigente.

No se dispone aún de pruebas reproducibles que permitan confirmar el funcionamiento integrado del brazo, la garra y sus controladores en MARTHA.

### Estado de los componentes

| Componente | Estado |
|---|---|
| Selección del brazo EB300 | Decisión aprobada |
| Arquitectura ROS 2 de referencia | Documentación identificada |
| Modelo MARTHA con torre y brazo | Antecedentes existentes; pendiente verificar |
| Integración URDF/Xacro | Pendiente de auditoría |
| Simulación en Gazebo | No validada |
| Control de articulaciones | No validado |
| Sistema de elevación | No validado |
| Control de garra | No validado |
| Integración ros2_control | No validada |
| Integración MoveIt 2 | Por verificar |
| Interfaces ROS 2 | Por verificar |
| Manipulación de objetos | Pendiente |

**Importante:** la existencia de un archivo o una configuración no significa que su funcionamiento haya sido comprobado.

---

## 4. Entorno de desarrollo

El entorno de referencia definido para el proyecto es:

| Herramienta | Versión o descripción |
|---|---|
| Sistema operativo | Ubuntu 22.04 LTS |
| Framework | ROS 2 Humble |
| Simulador | Gazebo, versión por confirmar |
| Lenguajes | Python, C++ |
| Modelado robótico | URDF / Xacro |
| Control | ros2_control |
| Planificación | MoveIt 2, pendiente de verificación |
| Entorno de trabajo | Visual Studio Code |
| Workspace | `~/ros2_ws` |

La instalación efectiva de dependencias y las versiones del entorno deben corroborarse en el equipo donde se ejecuta el proyecto.

### Workspace de referencia

```text
~/ros2_ws/
├── src/
│   ├── martha_nav/
│   ├── martha_nav_robotic_arm/
│   ├── marta_arm/
│   └── ...
├── build/
├── install/
└── log/
```

Esta estructura representa los paquetes mencionados en el desarrollo anterior. Se debe verificar su existencia y contenido real.

---

## 5. Arquitectura del sistema

La arquitectura se organiza conceptualmente en los siguientes componentes:

```text
MARTHA
│
├── Plataforma móvil
│   ├── Base robótica
│   ├── Sistema de locomoción
│   └── Navegación
│
├── Sistema de manipulación
│   ├── Estructura de soporte
│   ├── Sistema de elevación
│   ├── Brazo EB300
│   └── Garra / Gripper
│
├── Control robótico
│   ├── ROS 2
│   ├── ros2_control
│   ├── Controladores articulares
│   └── MoveIt 2 (por verificar)
│
└── Simulación
    ├── URDF / Xacro
    ├── Gazebo
    ├── Sensores virtuales
    └── Visualización
```

Esta es una arquitectura objetivo, no una representación de componentes ya validados.

### Criterios de diseño

- **Modularidad:** separar modelo, control, planificación y funciones de manipulación.
- **Reutilización:** aprovechar los desarrollos existentes de MILO.
- **Compatibilidad:** conservar las interfaces públicas necesarias para el resto del equipo.
- **Mantenibilidad:** permitir modificaciones aisladas sin afectar componentes independientes.
- **Validación incremental:** comprobar cada subsistema antes de realizar la integración completa.

---

## 6. Componentes principales

### 6.1. Plataforma MARTHA

MARTHA constituye la base móvil sobre la que se integrará el manipulador.

La integración debe considerar la ubicación del brazo, el soporte mecánico, las posibles colisiones y la estabilidad de la plataforma.

### 6.2. Brazo robótico EB300

Brazo seleccionado para su adaptación desde MILO.

Se requiere identificar y comprobar:

- Número de articulaciones y grados de libertad.
- Ejes y límites articulares.
- Modelos visuales y de colisión.
- Propiedades de masa e inercia.
- Controladores disponibles.
- Interfaces de comandos y estado.

Las características mecánicas específicas deben obtenerse del modelo y la documentación vigente.

### 6.3. Garra robótica

Actuador final encargado de realizar operaciones de agarre y liberación.

Funciones previstas:

- Apertura.
- Cierre.
- Control de posición o accionamiento según el mecanismo.
- Publicación del estado, según la interfaz implementada.
- Integración con las secuencias de manipulación.

### 6.4. Sistema de elevación

Mecanismo asociado al posicionamiento vertical del sistema manipulador.

Debe verificarse su implementación en MILO y su posible adaptación a MARTHA.

### 6.5. Control y planificación

Se contempla el uso de `ros2_control` para el control articular y MoveIt 2 para la planificación de movimientos, sujeto a la auditoría de los paquetes disponibles.

---

## 7. Archivos identificados

En conversaciones técnicas anteriores se mencionaron los siguientes archivos:

| Archivo | Función prevista |
|---|---|
| `martha_milo_single_column.urdf.xacro` | Modelo integrado de referencia |
| `martha_milo_single_column_module.xacro` | Módulo de soporte e integración |
| `martha.urdf.xacro` | Modelo de MARTHA |
| `martha_shortened.urdf.xacro` | Variante del modelo |
| `robot_arm_copy.xacro` | Modelo o módulo del brazo |
| `milo_elevator_module` | Módulo de elevación por localizar |
| `sim.launch.py` | Lanzamiento de simulación |

**Nota:** estos nombres son antecedentes de trabajo. Las rutas definitivas, su existencia actual y su vigencia deben verificarse directamente en el repositorio.

---

## 8. Preparación y diagnóstico del entorno

Los siguientes comandos permiten iniciar la inspección del proyecto.

### 8.1. Cargar ROS 2

```bash
source /opt/ros/humble/setup.bash
```

### 8.2. Acceder al workspace

```bash
cd ~/ros2_ws
```

### 8.3. Revisar los paquetes presentes

```bash
colcon list
```

### 8.4. Identificar modelos URDF/Xacro

```bash
find src -type f \( \
  -name "*.urdf" -o \
  -name "*.xacro" \
\)
```

### 8.5. Identificar archivos de lanzamiento

```bash
find src -type f \( \
  -name "*.launch.py" -o \
  -name "*.launch.xml" \
\)
```

### 8.6. Identificar configuraciones de control

```bash
find src -type f \( \
  -name "*.yaml" -o \
  -name "*.yml" \
\)
```

### 8.7. Compilar el workspace

Una vez revisadas las dependencias y los paquetes:

```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

La compilación debe registrarse como satisfactoria únicamente cuando termine sin errores.

---

## 9. Simulación en Gazebo

En el desarrollo anterior se utilizó como referencia el siguiente comando:

```bash
ros2 launch martha_nav sim.launch.py \
  robot:=martha_tower \
  drive:=mecanum \
  with_arm:=true \
  gui:=true \
  rviz:=false
```

**Estado:** comando histórico de referencia, no validado en la etapa actual.

Antes de considerarlo operativo se debe comprobar:

1. Existencia del paquete `martha_nav`.
2. Existencia y parámetros de `sim.launch.py`.
3. Generación correcta del modelo URDF.
4. Carga de MARTHA y sus componentes.
5. Ausencia de errores críticos y colisiones iniciales.
6. Disponibilidad de controladores.

---

## 10. Validación de ROS 2

Una vez iniciada correctamente la simulación, inspeccionar las interfaces disponibles.

### Nodos

```bash
ros2 node list
```

### Tópicos

```bash
ros2 topic list -t
```

### Servicios

```bash
ros2 service list -t
```

### Acciones

```bash
ros2 action list -t
```

### Controladores

Si está instalado y activo `ros2_control`:

```bash
ros2 control list_controllers
```

Las interfaces encontradas deben compararse con los requisitos de la arquitectura del equipo.

No se debe asumir la existencia de tópicos, servicios o acciones del brazo hasta comprobarlos.

---

## 11. Historial de desarrollo

### 2026-10-25 — Definición del alcance

Se estableció como objetivo adaptar a MARTHA el sistema de brazo y garra utilizado en MILO.

Se determinó comenzar con el inventario técnico y el diagnóstico de la simulación.

### 2026-10-25 — Decisión técnica D-001

**Decisión:** reutilizar el brazo robótico EB300 de MILO para MARTHA.

Alternativas consideradas:

1. Buscar un brazo robótico de código abierto con capacidad de carga de referencia de 2 kg.
2. Adaptar el desarrollo existente de MILO.

Se seleccionó la segunda alternativa para reducir el tiempo de desarrollo y aprovechar componentes previamente implementados.

La capacidad de carga de 2 kg fue un criterio de búsqueda, no una especificación validada del EB300.

### Antecedentes técnicos anteriores

Se discutieron modelos de MARTHA con torre de aluminio, columnas de soporte y brazo EB300.

También se revisaron configuraciones de Gazebo, ROS 2 y archivos Xacro.

Estos antecedentes constituyen información para el diagnóstico, pero no permiten confirmar que la última configuración esté completamente funcional.

### 2026-10-30 — Consolidación documental

Se actualiza el README con el alcance, la arquitectura prevista, el entorno, los antecedentes técnicos y el estado registrado del proyecto.

Esta actualización documental no representa una nueva versión de software validada.

---

## 12. Plan de desarrollo

### Fase 0 — Diagnóstico

- [ ] Identificar los paquetes reales de MILO y MARTHA.
- [ ] Revisar los archivos URDF/Xacro.
- [ ] Identificar controladores y archivos de configuración.
- [ ] Verificar el estado de la simulación.
- [ ] Elaborar un inventario de componentes reutilizables.

### Fase 1 — Integración mecánica virtual

- [ ] Adaptar el montaje del brazo EB300 a MARTHA.
- [ ] Comprobar articulaciones y límites.
- [ ] Revisar colisiones.
- [ ] Verificar masas e inercias.
- [ ] Validar la estructura completa en Gazebo.

### Fase 2 — Control articular

- [ ] Configurar o adaptar `ros2_control`.
- [ ] Activar los controladores correspondientes.
- [ ] Comprobar movimiento individual de articulaciones.
- [ ] Validar el sistema de elevación.
- [ ] Verificar publicación de estados.

### Fase 3 — Garra

- [ ] Integrar el mecanismo virtual de agarre.
- [ ] Implementar comandos de apertura y cierre.
- [ ] Comprobar límites y estados.
- [ ] Validar movimientos repetibles.

### Fase 4 — Planificación

- [ ] Verificar la disponibilidad de MoveIt 2.
- [ ] Configurar el grupo de planificación.
- [ ] Comprobar restricciones y colisiones.
- [ ] Planificar trayectorias.
- [ ] Ejecutar movimientos simulados.

### Fase 5 — Integración funcional

- [ ] Comprobar las interfaces requeridas por el equipo.
- [ ] Integrar percepción virtual si corresponde.
- [ ] Implementar secuencias de manipulación.
- [ ] Probar agarre, transporte y liberación.
- [ ] Documentar resultados reproducibles.

---

## 13. Criterios de aceptación

Una funcionalidad se considerará validada únicamente cuando tenga evidencia reproducible.

| Funcionalidad | Criterio de aceptación |
|---|---|
| Modelo URDF | Generación sin errores |
| Integración Gazebo | Carga completa sin errores críticos |
| Articulaciones | Movimiento controlado dentro de límites |
| Sistema de elevación | Desplazamiento simulado correcto |
| Garra | Apertura y cierre repetibles |
| ros2_control | Controladores activos y funcionales |
| MoveIt 2 | Planificación y ejecución verificables |
| Interfaces ROS 2 | Tipos y comportamiento comprobados |
| Manipulación | Secuencia completa demostrada |

Cada validación debe registrar como mínimo el comando ejecutado y el resultado obtenido.

---

## 14. Limitaciones actuales

- El alcance inmediato se limita al software y la simulación.
- No se ha validado la implementación física.
- No se ha completado la auditoría del repositorio.
- No se ha confirmado el funcionamiento de los controladores.
- No se ha verificado la compatibilidad completa entre MILO y MARTHA.
- No se dispone todavía de pruebas integradas de manipulación.
- Las especificaciones definitivas del brazo y la garra deben contrastarse con los modelos reales.

---

## 15. Documentación del proyecto

Se mantienen tres archivos principales para organizar el contexto y las decisiones.

| Documento | Propósito |
|---|---|
| `01_CONTEXTO.md` | Objetivos, entorno, arquitectura y restricciones |
| `02_DECISIONES.md` | Decisiones técnicas y justificaciones |
| `03_ESTADO.md` | Estado vigente, problemas y siguiente prioridad |
| `README.md` | Presentación general, estructura y guía de trabajo |

El README proporciona una visión general del proyecto.

El archivo `03_ESTADO.md` es la fuente principal para determinar qué funciona, qué está pendiente y cuál es el siguiente paso.

Las decisiones aprobadas se conservan en `02_DECISIONES.md`.

---

## 16. Referencias

### Arquitectura ROS 2 del equipo

https://alejapinzonf.github.io/Robot_arquitecture_ROS2/

### Documentación oficial

- ROS 2 Humble: https://docs.ros.org/en/humble/
- ros2_control: https://control.ros.org/
- MoveIt 2: https://moveit.picknik.ai/
- URDF: https://wiki.ros.org/urdf
- Xacro: https://github.com/ros/xacro

---

## 17. Próximo paso

**Prioridad inmediata: realizar el inventario del repositorio vigente.**

Se debe identificar la implementación del brazo EB300 de MILO y contrastarla con los componentes disponibles en MARTHA.

El resultado esperado es una relación verificable de:

1. Paquetes y archivos existentes.
2. Componentes reutilizables.
3. Componentes faltantes o incompatibles.
4. Interfaces ROS 2 disponibles.
5. Errores reproducibles.
6. Modificaciones necesarias para comenzar la integración.

No implementar nuevas funcionalidades antes de establecer el estado real del código existente.

---

**RoboCup 2027 — Desarrollo del sistema de manipulación robótica de MARTHA.**
