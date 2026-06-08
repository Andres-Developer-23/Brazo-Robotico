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

# Lista de todos los objetos agarrables del mundo
OBJETOS_DEF = ["CAJA_ROJA", "CILINDRO_AZUL", "ESFERA_VERDE", "CUBO_AMARILLO", "CUBO_NARANJA"]
objetos = []
for def_name in OBJETOS_DEF:
    nodo = robot.getFromDef(def_name)
    if nodo:
        objetos.append({
            "nodo": nodo,
            "trans": nodo.getField("translation"),
            "nombre": def_name
        })

grabbed = False
objeto_agarrado = None
ultima_pos = None

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
        
        # Buscar el objeto más cercano a la garra
        if not grabbed and punto_agarre:
            pos_garra = punto_agarre.getPosition()
            mejor_dist = float('inf')
            mejor_obj = None
            
            for obj in objetos:
                pos_obj = obj["nodo"].getPosition()
                dist = math.sqrt((pos_garra[0]-pos_obj[0])**2 + (pos_garra[1]-pos_obj[1])**2 + (pos_garra[2]-pos_obj[2])**2)
                if dist < mejor_dist:
                    mejor_dist = dist
                    mejor_obj = obj
            
            if mejor_dist < 1.2:
                grabbed = True
                objeto_agarrado = mejor_obj
                print("¡{} ATRAPADO! (distancia: {:.2f}m)".format(objeto_agarrado["nombre"], mejor_dist))
            else:
                print("Acerca más la garra (objeto más cercano a {:.2f}m)".format(mejor_dist))

    elif key == ord('S'):
        motor_gi.setVelocity(-VEL_GARRA)
        motor_gd.setVelocity(-VEL_GARRA)
        if grabbed and objeto_agarrado:
            grabbed = False
            if ultima_pos:
                objeto_agarrado["trans"].setSFVec3f(ultima_pos)
                objeto_agarrado["nodo"].setVelocity([0, 0, 0, 0, 0, 0])
            objeto_agarrado = None
            print("OBJETO SOLTADO.")

    # ── Sincronizar posición si está agarrada ─────────────────────────────────
    if grabbed and objeto_agarrado and punto_agarre:
        pos = punto_agarre.getPosition()
        pos[1] += 0.3  # offset para evitar colisión con el bounding box de la garra
        ultima_pos = list(pos)
        objeto_agarrado["trans"].setSFVec3f(pos)
        objeto_agarrado["nodo"].setVelocity([0, 0, 0, 0, 0, 0])
