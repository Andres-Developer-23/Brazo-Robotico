"""
Controlador para el brazo robótico de 3 segmentos + garra.

Motores y controles:
  motor_base    → ← / →      Rotación horizontal de la base
  motor_brazo_1 ↑ / ↓        Elevación del hombro
  motor_brazo_2 A / D         Flexión del codo (antebrazo)
  motor_brazo_3 Q / E         Rotación de la muñeca
  motor_garra   W / S         Abrir / cerrar garra (ambos dedos)
"""

from controller import Robot, Keyboard

# ── Configuración ──────────────────────────────────────────────────────────────
VEL_BASE   = 0.4   # rad/s — velocidad de rotación de la base
VEL_BRAZO  = 0.3   # rad/s — velocidad de los segmentos del brazo
VEL_GARRA  = 0.5   # rad/s — velocidad de apertura/cierre de la garra

# ── Inicialización del robot ───────────────────────────────────────────────────
robot    = Robot()
timestep = int(robot.getBasicTimeStep())

# ── Motor y sensor: BASE ──────────────────────────────────────────────────────
motor_base   = robot.getDevice("motor_base")
sensor_base  = robot.getDevice("sensor_base")
sensor_base.enable(timestep)
motor_base.setPosition(float('inf'))
motor_base.setVelocity(0.0)

# ── Motor y sensor: HOMBRO (brazo 1) ──────────────────────────────────────────
motor_b1   = robot.getDevice("motor_brazo_1")
sensor_b1  = robot.getDevice("sensor_brazo_1")
sensor_b1.enable(timestep)
motor_b1.setPosition(float('inf'))
motor_b1.setVelocity(0.0)

# ── Motor y sensor: CODO (brazo 2) ────────────────────────────────────────────
motor_b2   = robot.getDevice("motor_brazo_2")
sensor_b2  = robot.getDevice("sensor_brazo_2")
sensor_b2.enable(timestep)
motor_b2.setPosition(float('inf'))
motor_b2.setVelocity(0.0)

# ── Motor y sensor: MUÑECA (brazo 3) ──────────────────────────────────────────
motor_b3   = robot.getDevice("motor_brazo_3")
sensor_b3  = robot.getDevice("sensor_brazo_3")
sensor_b3.enable(timestep)
motor_b3.setPosition(float('inf'))
motor_b3.setVelocity(0.0)

# ── Motores y sensores: GARRA (dedo izq + dedo der sincronizados) ─────────────
motor_gi   = robot.getDevice("motor_garra_izq")
motor_gd   = robot.getDevice("motor_garra_der")
sensor_gi  = robot.getDevice("sensor_garra_izq")
sensor_gd  = robot.getDevice("sensor_garra_der")
sensor_gi.enable(timestep)
sensor_gd.enable(timestep)
motor_gi.setPosition(float('inf'))
motor_gd.setPosition(float('inf'))
motor_gi.setVelocity(0.0)
motor_gd.setVelocity(0.0)

# ── Teclado ───────────────────────────────────────────────────────────────────
keyboard = Keyboard()
keyboard.enable(timestep)

print("=== Brazo Robótico — Controles ===")
print("  ← / →   : Rotar base")
print("  ↑ / ↓   : Hombro (brazo 1)")
print("  A / D   : Codo   (brazo 2)")
print("  Q / E   : Muñeca (brazo 3)")
print("  W / S   : Garra  (abrir / cerrar)")
print("==================================")

# ── Bucle principal ───────────────────────────────────────────────────────────
while robot.step(timestep) != -1:
    key = keyboard.getKey()

    # Detener todos los motores por defecto
    motor_base.setVelocity(0.0)
    motor_b1.setVelocity(0.0)
    motor_b2.setVelocity(0.0)
    motor_b3.setVelocity(0.0)
    motor_gi.setVelocity(0.0)
    motor_gd.setVelocity(0.0)

    # ── BASE ──────────────────────────────────────────────────────────────────
    if key == Keyboard.LEFT:
        motor_base.setVelocity(VEL_BASE)
    elif key == Keyboard.RIGHT:
        motor_base.setVelocity(-VEL_BASE)

    # ── HOMBRO ────────────────────────────────────────────────────────────────
    elif key == Keyboard.UP:
        motor_b1.setVelocity(VEL_BRAZO)
    elif key == Keyboard.DOWN:
        motor_b1.setVelocity(-VEL_BRAZO)

    # ── CODO ──────────────────────────────────────────────────────────────────
    elif key == ord('A'):
        motor_b2.setVelocity(VEL_BRAZO)
    elif key == ord('D'):
        motor_b2.setVelocity(-VEL_BRAZO)

    # ── MUÑECA ────────────────────────────────────────────────────────────────
    elif key == ord('Q'):
        motor_b3.setVelocity(VEL_BRAZO)
    elif key == ord('E'):
        motor_b3.setVelocity(-VEL_BRAZO)

    # ── GARRA (ambos dedos sincronizados en espejo) ────────────────────────────
    elif key == ord('W'):
        motor_gi.setVelocity(VEL_GARRA)
        motor_gd.setVelocity(VEL_GARRA)
    elif key == ord('S'):
        motor_gi.setVelocity(-VEL_GARRA)
        motor_gd.setVelocity(-VEL_GARRA)
