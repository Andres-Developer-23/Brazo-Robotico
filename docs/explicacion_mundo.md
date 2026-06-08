# El Mundo del Brazo Robótico — Explicación Detallada para Exposición

## 1. ¿Qué es un "mundo" en Webots?

En Webots, un **mundo** es un archivo que describe por completo una simulación. No es solo un escenario 3D: contiene todos los objetos, sus posiciones, materiales, propiedades físicas, luces, cámaras, y la referencia al controlador que programa el comportamiento de los robots. Es el punto de entrada de cualquier simulación.

- **Formato:** VRML (Virtual Reality Modeling Language) con extensiones propias de Webots.
- **Versión del simulador:** R2025a.
- **Archivo principal:** `worlds/brazo_robotico.wbt` — 535 líneas de código.
- **Flujo de trabajo:** al abrir este archivo en Webots, el motor de simulación carga la escena, inicializa la física y ejecuta automáticamente el controlador Python asociado.

---

## 2. Configuración General de la Escena

### WorldInfo (línea 7-8)
```vrml
WorldInfo {}
```
Metadatos del mundo. En este caso está vacío, pero podría contener configuración de gravedad, color de fondo, paso de tiempo, etc. Se deja por defecto.

### Viewpoint (líneas 9-12)
```vrml
Viewpoint {
  orientation 0.0137 -0.0199 0.9997 1.208
  position    -4.78 -36.7 5.48
}
```
Define la **cámara virtual**. La posición `(-4.78, -36.7, 5.48)` es una vista en tercera persona elevada y alejada, ideal para ver toda la escena: el brazo robótico en el centro, los 5 objetos esparcidos alrededor, y el tanque contenedor a la derecha. La orientación con cuaternión apunta la cámara hacia el origen.

### TexturedBackground (líneas 13-14)
Fondo panorámico con texturas cúbicas de montañas. Webots descarga 6 imágenes HDR del repositorio oficial (derecha, izquierda, arriba, abajo, frontal, trasera) para crear un cielo envolvente realista.

### TexturedBackgroundLight (líneas 15-16)
Iluminación direccional que acompaña al fondo. Simula luz solar natural: una fuente direccional que proyecta sombras y da volumen a los objetos.

### RectangleArena (líneas 17-20)
```vrml
RectangleArena {
  translation 0.21 0 0
  floorSize 26 26
}
```
El suelo de la simulación: un rectángulo de **26×26 metros** ligeramente desplazado en X. Internamente, Webots genera un sólido con textura de parqué ajedrezado usando 4 mapas (color base, rugosidad, normales y oclusión) para dar un acabado realista.

---

## 3. El Brazo Robótico — DEF ROBOT1 (líneas 21-280)

```vrml
DEF ROBOT1 Robot {
  supervisor TRUE
  ...
  controller "robot_brazo"
}
```
El brazo es un nodo **Robot** con el flag `supervisor: TRUE`. Esto es fundamental: un robot normal solo controla sus propios dispositivos, pero un **Supervisor** tiene acceso privilegiado a todos los nodos del mundo. Puede leer y modificar posiciones, rotaciones, propiedades físicas de cualquier objeto en tiempo real. Esto es lo que permite el sistema de agarre.

El controlador asignado es `robot_brazo`, que Webots busca en `controllers/robot_brazo/robot_brazo.py`.

### 3.1 Base — DEF BASE (líneas 24-38)

```vrml
DEF BASE Solid {
  children [
    Pose {
      rotation 1 0 0 1.57079632679  # 90° en X
      children [ CadShape { url [ "../brazo-robotico/base.obj" ] } ]
    }
  ]
  name "base"
}
```
La base es un **Solid** estático (sin articulaciones). Es el punto de anclaje de todo el brazo.

- **Modelo 3D:** `brazo-robotico/base.obj` — modelado en Blender 4.0.2 como una plataforma circular.
- **Rotación:** el modelo original está horizontal (como se modeló en Blender), pero necesita rotarse 90° en X (`π/2 rad`) para quedar vertical y correctamente orientado en el mundo de Webots.
- **Función:** sostener toda la cadena cinemática y servir como base sólida para el primer HingeJoint.

### 3.2 Cadena Cinemática — 3 HingeJoints (líneas 39-275)

Una **cadena cinemática** es una secuencia de segmentos rígidos conectados por articulaciones. Aquí tenemos 3 segmentos idénticos (todos usan `brazo-1.obj`) conectados por **HingeJoint** — articulaciones de 1 grado de libertad que rotan en un solo eje.

La cadena funciona así:

```
Base (fija)
  └── HingeJoint (motor_base, eje Z) → rotación horizontal
       └── BRAZO1 (Solid)
            └── HingeJoint (motor_brazo_1, eje X) → hombro
                 └── BRAZO2 (Solid)
                      └── HingeJoint (motor_brazo_2, eje X) → codo
                           └── BRAZO3 (Solid)
                                └── HingeJoint (motor_brazo_3, eje X) → muñeca
                                     └── GARRA (Solid)
```

| Segmento | Motor | Eje de rotación | Límites | Anclaje (relativo) |
|---|---|---|---|---|
| Base → Brazo 1 | `motor_base` | Z (horizontal) | Ilimitado (360° continuos) | (0.024, -0.303, 1.342) |
| Brazo 1 → Brazo 2 | `motor_brazo_1` | X (vertical) | ±90° (-1.57 a 1.57 rad) | (0.025, -0.284, 5.498) |
| Brazo 2 → Brazo 3 | `motor_brazo_2` | X (vertical) | ±90° | (0.025, -0.284, 5.498) |
| Brazo 3 → Garra | `motor_brazo_3` | X (vertical) | ±90° | (0.025, -0.284, 5.498) |

**Detalles importantes:**

- La **base rota 360°** continua (sin límite de posición), lo que permite orientar el brazo en cualquier dirección horizontal.
- Los **3 segmentos del brazo** tienen límite de ±90° para evitar configuraciones irreales o autocolisiones.
- Cada segmento incluye un `PositionSensor` para que el controlador pueda leer la posición angular actual.
- El `anchor` de cada HingeJoint define el punto físico de rotación. Como los 3 segmentos usan la misma malla, los anchors tienen el mismo offset relativo (0.025, -0.284, 5.498), pero aplicado en la posición transformada del segmento padre.
- Cada segmento tiene un `boundingObject` cilíndrico (radio 0.25m, alto 5.0m) para detección de colisiones. Sin estos, el brazo atravesaría los objetos agarrados.

### 3.3 Garra — DEF GARRA (líneas 140-230)

```vrml
DEF GARRA Solid {
  ...
  children [
    Pose { ... CadShape { url [ "../brazo-robotico/garra.obj" ] } }
    DEF PUNTO_AGARRE Connector { ... }
    HingeJoint { ... }  # dedo_izq
    HingeJoint { ... }  # dedo_der
  ]
}
```
La garra es el **efector final** del brazo. Está compuesta por:

- **Malla 3D:** `garra.obj` — pinza de 2 dedos modelada en Blender.
- **Palma:** tiene un `boundingObject` en forma de caja de 1.1×0.4×3.0m para colisiones.
- **Dedo izquierdo:** HingeJoint con motor `motor_garra_izq`, rota en eje Y positivo. Anclado en (-0.442, -0.264, 3.249). Su bounding box es 0.2×0.2×2.6m.
- **Dedo derecho:** HingeJoint con motor `motor_garra_der`, rota en eje Y negativo. Anclado en (0.467, -0.264, 3.249). Mismo bounding box.

Los dos dedos rotan en **direcciones opuestas** (eje Y positivo vs negativo). Cuando ambos motores giran con velocidad positiva, los dedos se cierran (pinza se aprieta). Con velocidad negativa, se abren.

### 3.4 Punto de Agarre — DEF PUNTO_AGARRE (líneas 154-161)

```vrml
DEF PUNTO_AGARRE Connector {
  translation 0 -0.264 3.0
  name "conector_garra"
  type "symmetric"
  boundingObject Sphere { radius 0.001 }
}
```
Este es un nodo **Connector** de tipo simétrico. Originalmente se diseñó para agarre magnético (Webots Connector permite "pegar" físicamente dos objetos), pero en la versión actual del proyecto:

- Es solo un **punto de referencia geométrico** invisible.
- El controlador Python usa `getPosition()` de este nodo para calcular distancias.
- Su tamaño es minúsculo (esfera de 0.001m de radio) para no interferir con la física.
- Está situado en `(0, -0.264, 3.0)` relativo a la garra → justo en la punta del efector, entre los dos dedos.

La tolerancia de distancia y eje está configurada al máximo (`distanceTolerance 50.0`, `axisTolerance π`) porque ya no se usa para detección física, sino puramente como marcador de posición.

---

## 4. Objetos Agarrables (líneas 282-442)

Hay **5 objetos** que el brazo puede agarrar. Todos comparten la misma estructura:

```vrml
DEF NOMBRE Robot {
  controller "<none>"
  translation X Y Z
  children [
    Connector { ... }          # Referencia para el Supervisor
    Shape {
      appearance PBRAppearance { ... }  # Material realista
      geometry ...                      # Forma
    }
  ]
  boundingObject ...   # Colisiones
  physics Physics { density -1 mass 0.001 }  # Física ultraligera
}
```

Son nodos **Robot** con `controller "<none>"`. ¿Por qué Robot y no Solid? Porque los dispositivos como Connector solo funcionan dentro de nodos Robot. Al ser robots sin controlador, son pasivos pero Webots activa sus físicas y conectores.

La masa de 0.001 kg es intencional: objetos muy livianos para que el brazo pueda moverlos sin esfuerzo y sin romper las restricciones físicas del motor ODE.

### Los 5 objetos en detalle:

| DEF | Nombre | Geometría | Color (RGB) | Rugosidad | Metalizado | Posición (X,Y,Z) |
|---|---|---|---|---|---|---|
| `CAJA_ROJA` | caja_roja | Cubo 0.6m | 0.8, 0.2, 0.2 (rojo) | 0.5 | 0 | (0, 5, 1) |
| `CILINDRO_AZUL` | cilindro_azul | Cilindro h=0.8 r=0.35 | 0.1, 0.3, 0.9 (azul) | 0.4 | 0.1 | (3, 4, 1) |
| `ESFERA_VERDE` | esfera_verde | Esfera r=0.4 | 0.1, 0.8, 0.2 (verde) | 0.6 | 0 | (-3, 4, 1) |
| `CUBO_AMARILLO` | cubo_amarillo | Cubo 0.7m | 0.95, 0.85, 0.1 (amarillo) | 0.5 | 0 | (0, 7, 1) |
| `CUBO_NARANJA` | cubo_naranja | Cubo 0.5×0.8×0.5 | 0.95, 0.5, 0.05 (naranja) | 0.3 | 0.2 | (-4, 7, 1) |

**Disposición espacial:**
- 3 objetos cerca del brazo (rojo, azul, verde) a alturas Y=4-5 — accesibles directamente.
- 2 objetos más lejos (amarillo, naranja) a Y=7 — requieren estirar más el brazo.
- El cubo naranja es el único rectangular (0.5×0.8×0.5), presentando un desafío de agarre diferente.

---

## 5. Tanque Contenedor (líneas 444-534)

```vrml
# Ubicación: (8, 0, 0)
# Piso:   caja 4×4×0.3m
# Pared frontal: 4×0.2×2.6m en Y=2.1
# Pared trasera: 4×0.2×2.6m en Y=-2.1
# Pared izq:     0.2×4.4×2.6m en X=6.1
# Pared der:     0.2×4.4×2.6m en X=9.9
```

El tanque es un contenedor de acero situado a **8 metros del brazo** en dirección X positiva. Está compuesto por 5 sólidos independientes:

- **1 piso:** base de 4×4×0.3m a altura 0.15m.
- **4 paredes:** 2.6m de alto, dejando la parte superior abierta.
  - Frontal y trasera: 4m de ancho × 0.2m de grosor.
  - Laterales: 0.2m de grosor × 4.4m de ancho (las paredes laterales cubren todo el frente incluyendo el grosor de las paredes frontal/trasera).
- Dimensiones internas aproximadas: **4×4×2.6m**, suficiente para almacenar todos los objetos.

Todos los sólidos tienen `locked TRUE` (cuerpos cinemáticos). Esto significa que Webots no calcula su física (gravedad, colisiones dinámicas), pero siguen siendo obstáculos sólidos: los objetos pueden chocar contra ellos y quedarse dentro. Es más eficiente que darles masa (inicialmente tenían 500 kg cada uno).

El material es **acero**: color gris oscuro (0.25, 0.28, 0.32), rugosidad 0.8 (superficie mate), metalizado 0.6 (reflectante).

---

## 6. Controlador Python — `robot_brazo.py` (157 líneas)

### 6.1 Concepto: Supervisor vs Robot

Un robot normal solo accede a sus propios dispositivos (motores, sensores). Un **Supervisor** puede acceder a cualquier nodo del mundo. Esto es esencial para el agarre: necesitamos leer la posición de `PUNTO_AGARRE` y modificar la posición de los objetos agarrables en tiempo real.

### 6.2 Inicialización (líneas 14-66)

```python
robot = Supervisor()
timestep = int(robot.getBasicTimeStep())
```

- 6 motores configurados en **modo velocidad infinita**: `setPosition(float('inf'))` + `setVelocity(0.0)`. Esto permite controlar velocidad en vez de posición, dando control manual continuo.
- 6 sensores de posición habilitados con `enable(timestep)`.
- 5 objetos referenciados por su DEF name mediante `robot.getFromDef()`.
- Referencia al `PUNTO_AGARRE` para calcular distancias.

### 6.3 Sistema de Agarre (líneas 116-157)

**Al presionar W (agarrar):**

```python
if not grabbed and punto_agarre:
    pos_garra = punto_agarre.getPosition()  # Posición 3D del efector
    mejor_dist = float('inf')

    for obj in objetos:
        pos_obj = obj["nodo"].getPosition()
        # Distancia Euclidiana 3D:
        dist = √((x₁-x₂)² + (y₁-y₂)² + (z₁-z₂)²)
        if dist < mejor_dist:
            mejor_dist = dist
            mejor_obj = obj

    if mejor_dist < 1.2:  # ¿Suficientemente cerca?
        grabbed = True
        objeto_agarrado = mejor_obj
```

1. Obtiene la posición 3D del `PUNTO_AGARRE` (punta de la garra).
2. Recorre los 5 objetos calculando distancia Euclidiana.
3. Si el más cercano está a **menos de 1.2 metros**, lo agarra.

**Durante el agarre (cada frame):**

```python
if grabbed and objeto_agarrado and punto_agarre:
    pos = punto_agarre.getPosition()
    pos[1] += 0.3  # Offset Y para evitar colisión con bounding box de la garra
    objeto_agarrado["trans"].setSFVec3f(pos)     # Sincroniza posición
    objeto_agarrado["nodo"].setVelocity([0]*6)    # Frena vibraciones
```

El objeto se "teletransporta" frame a frame a la posición de la garra. El offset de +0.3m en Y evita que choque con el bounding box de la palma. El `setVelocity([0]*6)` evita vibraciones que antes hacían que el objeto escapara volando.

**Al presionar S (soltar):**

```python
if grabbed and objeto_agarrado:
    grabbed = False
    if ultima_pos:
        objeto_agarrado["trans"].setSFVec3f(ultima_pos)  # Restaura posición
        objeto_agarrado["nodo"].setVelocity([0]*6)         # Frena
```

Restaura la última posición conocida del objeto (donde estaba antes de soltar) y lo frena completamente. Sin esto, el objeto saldría disparado por la inercia acumulada.

### 6.4 Mapa Completo de Controles

| Tecla | Efecto | Motor | Velocidad |
|---|---|---|---|
| ← | Rotar base sentido horario | `motor_base` | 0.4 rad/s |
| → | Rotar base sentido antihorario | `motor_base` | -0.4 rad/s |
| ↑ | Brazo 1 sube (hombro) | `motor_brazo_1` | 0.3 rad/s |
| ↓ | Brazo 1 baja (hombro) | `motor_brazo_1` | -0.3 rad/s |
| A | Brazo 2 sube (codo) | `motor_brazo_2` | 0.3 rad/s |
| D | Brazo 2 baja (codo) | `motor_brazo_2` | -0.3 rad/s |
| Q | Brazo 3 sube (muñeca) | `motor_brazo_3` | 0.3 rad/s |
| E | Brazo 3 baja (muñeca) | `motor_brazo_3` | -0.3 rad/s |
| **W** | Cierra garra + agarra objeto | `motor_garra_izq/der` | 0.5 rad/s |
| **S** | Abre garra + suelta objeto | `motor_garra_izq/der` | -0.5 rad/s |

Las velocidades están calibradas para dar un control suave: la base gira más rápido (0.4) porque necesita cubrir 360°; los brazos son más lentos (0.3) para permitir precisión; la garra es la más rápida (0.5) para cerrar/abrir ágilmente.

---

## 7. Animación Grabada para Web (JSON, 2388 frames)

```json
{
  "basicTimeStep": 32,
  "frames": [
    {"time": 0, "updates": [...]},
    {"time": 32, "updates": [...]},
    ...
    {"time": 76352, "updates": [...]}
  ]
}
```

El archivo `brazo_robotico.json` contiene una animación pre-grabada de **2388 keyframes** a **32ms por frame** → aproximadamente **76 segundos** de duración.

Cada frame contiene una lista de `updates` que modifican la posición y rotación de nodos específicos, identificados por su **ID numérico**:

| ID | Nodo | Qué se anima |
|---|---|---|
| 158 | brazo_1 | translation + rotation |
| 165 | brazo_2 | translation + rotation |
| 172 | brazo_3 | translation + rotation |
| 179 | garra | translation + rotation |
| 188 | dedo_izq | translation + rotation |
| 196 | dedo_der | translation + rotation |
| 212 | caja_roja | translation + rotation (es agarrada y movida) |
| 220 | cilindro_azul | translation + rotation (es agarrado y movido) |
| 236 | cubo_amarillo | translation + rotation (es agarrado y movido) |

La animación muestra una secuencia completa: el brazo se mueve hacia cada objeto, lo agarra, lo lleva al tanque y lo suelta. Es una demostración pregrabada del funcionamiento del proyecto.

---

## 8. Visualización Web (X3D + HTML + CSS)

### brazo_robotico.w3d (25 líneas)
Escena en formato **X3D** (XML), que Webots genera automáticamente para exportar la simulación a la web. Contiene:

- Posiciones y rotaciones iniciales de todos los sólidos.
- Geometrías completas (incluyendo viseras de los meshes OBJ).
- URLs de texturas de fondo (montañas HDR).
- Materiales PBR de cada objeto.

Las mallas 3D se referencian desde `meshes/` (copias locales de los OBJ para que funcionen sin el proyecto original).

### brazo_robotico.html (26 líneas)
```html
<webots-view data-thumbnail=brazo_robotico.jpg
             data-scene=brazo_robotico.w3d
             data-animation=brazo_robotico.json>
</webots-view>
```
Carga el componente `WebotsView.js` R2025a desde el CDN de Cyberbotics (`https://cyberbotics.com/wwi/R2025a/WebotsView.js`). Este componente:

1. Carga la escena X3D (geometrías estáticas).
2. Carga la animación JSON (keyframes).
3. Reproduce la simulación en el navegador con controles de reproducción.

### brazo_robotico.css (92 líneas)
Diseño responsivo con:

- Barra superior oscura (#34495e) con logo de Webots y título.
- Contenedor de vista al 80% del alto de pantalla, centrado horizontalmente.
- Área de descripción (20% restante).
- Barra inferior fija con enlace a la guía de usuario de Webots.

---

## 9. Modelos 3D — Blender 4.0.2

El proyecto incluye **3 piezas** modeladas en Blender y exportadas como OBJ + MTL:

| Pieza | Archivo | Función |
|---|---|---|
| Base | `brazo-robotico/base.obj` | Plataforma circular de apoyo |
| Segmento | `brazo-robotico/brazo-1.obj` | Brazo único, instanciado 3 veces |
| Garra | `brazo-robotico/garra.obj` | Pinza de 2 dedos |

**Nota sobre los MTL:** Los archivos `.mtl` son mínimos (solo cabecera de Blender) porque los materiales se definen directamente en Webots mediante el nodo `PBRAppearance` (color, rugosidad, metalizado). Esto permite cambiar materiales sin modificar los modelos 3D.

**Duplicación de mallas:** Los OBJ aparecen en 3 ubicaciones:

| Ubicación | Propósito |
|---|---|
| `brazo-robotico/` | Originales, referenciados por el `.wbt` |
| `worlds/meshes/` | Copias para la exportación web (X3D) |
| `worlds/` | Copias adicionales (por compatibilidad) |

---

## 10. Despliegue en webots.cloud

### Dockerfile (4 líneas)
```dockerfile
FROM cyberbotics/webots.cloud:R2025a-ubuntu22.04
ARG PROJECT_PATH
RUN mkdir -p $PROJECT_PATH
COPY . $PROJECT_PATH
```
Usa la imagen oficial de webots.cloud con Ubuntu 22.04 y Webots R2025a. Copia todo el proyecto al contenedor.

### webots.yml (3 líneas)
```yaml
publish: true
type: demo
dockerCompose:theia:webots-project/controllers/robot_brazo/
```
- `publish: true` → visible en webots.cloud.
- `type: demo` → simulación interactiva (no solo visualización).
- `theia: ...` → habilita el IDE Theia en el navegador, permitiendo al usuario editar el controlador Python y controlar el brazo por teclado en vivo desde la web.

---

## 11. Historia Evolutiva — 37 Commits

El proyecto pasó por varias etapas de desarrollo. Aquí están las más importantes:

### Fase 1: Estructura Inicial (commits 1-3)
- Creación del proyecto con modelos 3D base.
- Primer esqueleto del mundo Webots.

### Fase 2: Cadena Cinemática (commits 4-7)
- Inicialmente se intentaron **2 brazos independientes**, pero se fusionaron en una sola cadena cinemática de 3 segmentos.
- Se añadió la garra como efector final.
- Se corrigieron separaciones y alineaciones de ejes.

### Fase 3: Control por Teclado (commits 8-11)
- Implementación del controlador Python.
- Control de todos los motores desde el teclado.
- La base se configuró para rotación continua de 360°.

### Fase 4: Sistema de Agarre (commits 12-25) — **La fase más iterativa**
- **Versión 1:** Connector magnético (W bloquea, S suelta). Funcionaba pero era inestable.
- **Versión 2:** Ajustes de tolerancia (50m de alcance → "rayo tractor").
- **Versión 3:** Reducción de masa a 1g y bounding boxes minúsculos para evitar explosiones físicas.
- **Versión 4:** **Supervisor API** — se abandona el Connector físico. El controlador sincroniza posición manualmente. Agarre 100% estable.
- **Versión 5:** Corrección de vibraciones y rebotes al soltar.

### Fase 5: Más Objetos y Tanque (commits 26-32)
- Se añaden cilindro, esfera y 2 cubos adicionales (total: 5 objetos).
- Se construye el tanque contenedor (inicialmente con masa 500kg, luego `locked TRUE`).

### Fase 6: Preparación para Web (commits 33-37)
- Ajustes finales de boundingObjects.
- Grabación de animación (2388 frames).
- Dockerfile + webots.yml para webots.cloud.
- README final.

---

## 12. Estado Actual y Trabajo Futuro

### Completado ✓
- ✓ Modelado 3D de base, segmentos y garra en Blender 4.0.2.
- ✓ Cadena cinemática funcional de 4 grados de libertad (base rotatoria + 3 segmentos).
- ✓ Garra con 2 dedos sincronizados.
- ✓ Control manual completo por teclado (6 motores, 10 teclas).
- ✓ Agarre físico de 5 objetos de diferentes formas y tamaños.
- ✓ Tanque contenedor con paredes sólidas para depositar objetos.
- ✓ Animación grabada (76 segundos, 2388 frames) reproducible en navegador.
- ✓ Despliegue listo para webots.cloud (Docker + webots.yml).

### Pendiente ✗
- ✗ **Cinemática Inversa (IK):** actualmente el brazo se controla articulación por articulación. Con IK, se podría decir "ve a la posición X,Y,Z" y el brazo calcularía automáticamente los ángulos de cada motor. Esto permitiría programar trayectorias complejas.
- ✗ **Control autónomo:** rutinas preprogramadas como "recoge todos los objetos y llévalos al tanque en orden" sin intervención del usuario.
- ✗ **Robot window interactiva:** una interfaz gráfica dentro de Webots con sliders, botones y visualización de estado, en lugar de depender solo del teclado.

---

## 13. Diagrama de Árbol del Mundo

```
brazo_robotico.wbt
│
├── WorldInfo
├── Viewpoint
├── TexturedBackground
├── TexturedBackgroundLight
│
├── RectangleArena (suelo 26×26m)
│
├── DEF ROBOT1 (Robot, supervisor TRUE)
│   ├── DEF BASE (Solid)
│   │   └── CadShape ─── base.obj
│   │
│   ├── HingeJoint ─── motor_base (eje Z, 360°)
│   │   └── DEF BRAZO1 (Solid)
│   │       ├── CadShape ─── brazo-1.obj
│   │       ├── boundingObject (cilindro r=0.25 h=5.0)
│   │       │
│   │       ├── HingeJoint ─── motor_brazo_1 (eje X, ±90°)
│   │       │   └── DEF BRAZO2 (Solid)
│   │       │       ├── CadShape ─── brazo-1.obj
│   │       │       ├── boundingObject (cilindro r=0.25 h=5.0)
│   │       │       │
│   │       │       ├── HingeJoint ─── motor_brazo_2 (eje X, ±90°)
│   │       │       │   └── DEF BRAZO3 (Solid)
│   │       │       │       ├── CadShape ─── brazo-1.obj
│   │       │       │       ├── boundingObject (cilindro r=0.25 h=5.0)
│   │       │       │       │
│   │       │       │       ├── HingeJoint ─── motor_brazo_3 (eje X, ±90°)
│   │       │       │       │   └── DEF GARRA (Solid)
│   │       │       │       │       ├── CadShape ─── garra.obj
│   │       │       │       │       ├── boundingObject (caja 1.1×0.4×3.0)
│   │       │       │       │       ├── DEF PUNTO_AGARRE (Connector)
│   │       │       │       │       │
│   │       │       │       │       ├── HingeJoint ─── motor_garra_izq
│   │       │       │       │       │   └── dedo_izq (Solid)
│   │       │       │       │       │       └── boundingObject (caja 0.2×0.2×2.6)
│   │       │       │       │       │
│   │       │       │       │       └── HingeJoint ─── motor_garra_der
│   │       │       │       │           └── dedo_der (Solid)
│   │       │       │       │               └── boundingObject (caja 0.2×0.2×2.6)
│   │
│   └── controller: "robot_brazo" → robot_brazo.py
│
├── DEF CAJA_ROJA (Robot, masa 0.001kg) ─── posición (0, 5, 1)
├── DEF CILINDRO_AZUL (Robot, masa 0.001kg) ─── posición (3, 4, 1)
├── DEF ESFERA_VERDE (Robot, masa 0.001kg) ─── posición (-3, 4, 1)
├── DEF CUBO_AMARILLO (Robot, masa 0.001kg) ─── posición (0, 7, 1)
├── DEF CUBO_NARANJA (Robot, masa 0.001kg) ─── posición (-4, 7, 1)
│
├── tanque_piso (Solid, locked) ─── caja 4×4×0.3
├── tanque_pared_front (Solid, locked) ─── caja 4×0.2×2.6
├── tanque_pared_back (Solid, locked) ─── caja 4×0.2×2.6
├── tanque_pared_izq (Solid, locked) ─── caja 0.2×4.4×2.6
└── tanque_pared_der (Solid, locked) ─── caja 0.2×4.4×2.6
```
