# Brazo Robótico

Simulación de un brazo robótico en [Webots R2025a](https://cyberbotics.com/). El modelo 3D de la base fue creado en Blender 4.0.2 y se encuentra en una etapa inicial.

![Captura de la simulación](worlds/.brazo_robotico.jpg)

## Tecnologías

- **Webots R2025a** — simulador de robots open-source
- **Blender 4.0.2** — modelado 3D
- **Formato 3D:** OBJ + MTL

## Estructura del proyecto

```
brazo_robotico/
├── brazo-robotico/          # Modelos 3D del brazo
│   ├── base.obj             # Malla 3D de la base
│   └── base.mtl             # Materiales de la base
├── worlds/                  # Escenarios de Webots
│   ├── brazo_robotico.wbt   # Mundo principal de la simulación
│   ├── .brazo_robotico.wbproj
│   └── .brazo_robotico.jpg  # Preview de la simulación
└── README.md
```

## Requisitos previos

- [Webots R2025a](https://cyberbotics.com/#download) instalado

## Cómo ejecutar

1. Abre Webots.
2. Ve a `File > Open World...` y selecciona `worlds/brazo_robotico.wbt`.
3. **Corrige la ruta del modelo 3D** (solo la primera vez):
   - En el árbol de escena, expande `base` → `children` → `CadShape`.
   - En el campo `url`, cambia las rutas UUID (ej. `../../../1508fe4c/base.obj`) por `../../brazo-robotico/base.obj`.
   - También puedes hacer clic derecho en `CadShape`, seleccionar "Pick CAD file..." y elegir `brazo-robotico/base.obj`.
4. La simulación mostrará la base del brazo sobre el escenario rectangular.

## Estado del proyecto

Proyecto en etapa inicial. Actualmente incluye:

- [x] Base del brazo modelada en 3D
- [x] Escenario Webots con fondo texturizado y piso
- [ ] Segmentos del brazo (húmero, antebrazo, etc.)
- [ ] Articulaciones y motores
- [ ] Controlador (Python)
- [ ] Pinza o efector final

## Próximos pasos

- Modelar los segmentos restantes del brazo en Blender
- Definir articulaciones rotacionales con `HingeJoint` en Webots
- Escribir un controlador en Python para el movimiento
- Agregar un gripper o efector final

## Contribuciones

Las contribuciones son bienvenidas. Para colaborar:

1. **Reporta issues** — abre un issue describiendo el bug o la mejora.
2. **Fork** el repositorio y crea una rama descriptiva:
   - `feature/nombre` para nuevas funcionalidades
   - `fix/nombre` para correcciones
   - `docs/nombre` para documentación
3. **Desarrolla** manteniendo la estructura de directorios existente. Si agregas modelos 3D, documenta el archivo fuente de Blender.
4. **Commit** con mensajes descriptivos en español. Ejemplos:
   - `Agrega controlador Python para el brazo`
   - `Corrige ruta del modelo base.obj en el mundo Webots`
   - `Actualiza modelo 3D del húmero con nuevas geometrías`
5. **Abre un Pull Request** a la rama `main` describiendo los cambios.

### Entorno de desarrollo

- Webots R2025a
- Blender 4.0.2 (para modelos 3D)
- Python 3.x (para controladores)

### Código de conducta

Este proyecto sigue el [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Al participar, se espera que mantengas un entorno respetuoso e inclusivo.

## Licencia

Este proyecto no cuenta con licencia definida actualmente.
