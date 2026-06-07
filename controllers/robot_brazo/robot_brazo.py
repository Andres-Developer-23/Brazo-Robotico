from controller import Robot, Keyboard

robot = Robot()
timestep = int(robot.getBasicTimeStep())

name = robot.getName()
if name == "robot_brazo_1":
    motor1 = robot.getDevice("motor_brazo_1")
    sensor1 = robot.getDevice("sensor_brazo_1")
    motor2 = robot.getDevice("motor_brazo2_1")
    sensor2 = robot.getDevice("sensor_brazo2_1")
    key_m1_up = Keyboard.UP
    key_m1_down = Keyboard.DOWN
    key_m2_up = ord('A')
    key_m2_down = ord('D')
else:
    motor1 = robot.getDevice("motor_brazo_2")
    sensor1 = robot.getDevice("sensor_brazo_2")
    motor2 = robot.getDevice("motor_brazo2_2")
    sensor2 = robot.getDevice("sensor_brazo2_2")
    key_m1_up = ord('W')
    key_m1_down = ord('S')
    key_m2_up = ord('E')
    key_m2_down = ord('Q')

sensor1.enable(timestep)
sensor2.enable(timestep)
motor1.setPosition(float('inf'))
motor1.setVelocity(0.0)
motor2.setPosition(float('inf'))
motor2.setVelocity(0.0)

keyboard = Keyboard()
keyboard.enable(timestep)

while robot.step(timestep) != -1:
    key = keyboard.getKey()
    if key == key_m1_up:
        motor1.setVelocity(0.3)
        motor2.setVelocity(0.0)
    elif key == key_m1_down:
        motor1.setVelocity(-0.3)
        motor2.setVelocity(0.0)
    elif key == key_m2_up:
        motor2.setVelocity(0.3)
        motor1.setVelocity(0.0)
    elif key == key_m2_down:
        motor2.setVelocity(-0.3)
        motor1.setVelocity(0.0)
    else:
        motor1.setVelocity(0.0)
        motor2.setVelocity(0.0)
