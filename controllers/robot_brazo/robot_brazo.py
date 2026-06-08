"""
Controlador para el brazo robótico de 3 segmentos + garra usando Supervisor.
"""

from controller import Supervisor, Keyboard
import math

# ── Configuración ──────────────────────────────────────────────────────────────
VEL_BASE   = 0.4
VEL_BRAZO  = 0.3
VEL_GARRA  = 0.5

# ── Inicialización del robot ───────────────────────────────────────────────────
robot    = Supervisor()
timestep = int(robot.getBasicTimeStep())

# ── Motores ──────────────────────────────────────────────────────
motor_base   = robot.getDevice("motor_base")
sensor_base  = robot.getDevice("sensor_base")
sensor_base.enable(timestep)
motor_base.setPosition(float('inf'))
motor_base.setVelocity(0.0)

motor_b1   = robot.getDevice("motor_brazo_1")
sensor_b1  = robot.getDevice("sensor_brazo_1")
sensor_b1.enable(timestep)
motor_b1.setPosition(float('inf'))
motor_b1.setVelocity(0.0)

motor_b2   = robot.getDevice("motor_brazo_2")
sensor_b2  = robot.getDevice("sensor_brazo_2")
sensor_b2.enable(timestep)
motor_b2.setPosition(float('inf'))
motor_b2.setVelocity(0.0)

motor_b3   = robot.getDevice("motor_brazo_3")
sensor_b3  = robot.getDevice("sensor_brazo_3")
sensor_b3.enable(timestep)
motor_b3.setPosition(float('inf'))
motor_b3.setVelocity(0.0)

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

# ── Nodos para Agarre Supervisor ──────────────────────────────────────────────
punto_agarre = robot.getFromDef("PUNTO_AGARRE")
caja_roja = robot.getFromDef("CAJA_ROJA")
caja_trans = None
ultima_pos = None
if caja_roja:
    caja_trans = caja_roja.getField("translation")

grabbed = False

# ── Teclado ───────────────────────────────────────────────────────────────────
keyboard = Keyboard()
keyboard.enable(timestep)

print("=== Brazo Robótico — Controles ===")
print("  ← / →   : Rotar base")
print("  ↑ / ↓   : Hombro (brazo 1)")
print("  A / D   : Codo   (brazo 2)")
print("  Q / E   : Muñeca (brazo 3)")
print("  W / S   : Garra  (atrapar / soltar)")
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

    if key == Keyboard.LEFT:
        motor_base.setVelocity(VEL_BASE)
    elif key == Keyboard.RIGHT:
        motor_base.setVelocity(-VEL_BASE)

    elif key == Keyboard.UP:
        motor_b1.setVelocity(VEL_BRAZO)
    elif key == Keyboard.DOWN:
        motor_b1.setVelocity(-VEL_BRAZO)

    elif key == ord('A'):
        motor_b2.setVelocity(VEL_BRAZO)
    elif key == ord('D'):
        motor_b2.setVelocity(-VEL_BRAZO)

    elif key == ord('Q'):
        motor_b3.setVelocity(VEL_BRAZO)
    elif key == ord('E'):
        motor_b3.setVelocity(-VEL_BRAZO)

    elif key == ord('W'):
        motor_gi.setVelocity(VEL_GARRA)
        motor_gd.setVelocity(VEL_GARRA)
        
        # Intentar atrapar si no está atrapada
        if not grabbed and caja_roja and punto_agarre:
            pos_garra = punto_agarre.getPosition()
            pos_caja = caja_roja.getPosition()
            dist = math.sqrt((pos_garra[0]-pos_caja[0])**2 + (pos_garra[1]-pos_caja[1])**2 + (pos_garra[2]-pos_caja[2])**2)
            
            if dist < 1.2:  # Solo agarra si la garra está tocando la caja
                grabbed = True
                print("¡CAJA ATRAPADA! (distancia: {:.2f}m)".format(dist))
            else:
                print("Acerca más la garra a la caja (distancia actual: {:.2f}m)".format(dist))

    elif key == ord('S'):
        motor_gi.setVelocity(-VEL_GARRA)
        motor_gd.setVelocity(-VEL_GARRA)
        if grabbed:
            grabbed = False
            # Fijar la caja exactamente en la última posición y detener su física
            if caja_trans and ultima_pos:
                caja_trans.setSFVec3f(ultima_pos)
                caja_roja.resetPhysics()
            print("CAJA SOLTADA.")

    # ── Sincronizar posición si está agarrada ─────────────────────────────────
    if grabbed and caja_trans and punto_agarre:
        pos = punto_agarre.getPosition()
        ultima_pos = list(pos)  # Guardar última posición conocida
        caja_trans.setSFVec3f(pos)
        caja_roja.resetPhysics()
