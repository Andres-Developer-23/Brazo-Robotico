from controller import Robot, Keyboard

robot = Robot()
timestep = int(robot.getBasicTimeStep())

motor1 = robot.getDevice("motor_brazo_1")
sensor1 = robot.getDevice("sensor_brazo_1")
sensor1.enable(timestep)
motor1.setPosition(float('inf'))
motor1.setVelocity(0.0)

motor2 = robot.getDevice("motor_brazo2_1")
sensor2 = robot.getDevice("sensor_brazo2_1")
sensor2.enable(timestep)
motor2.setPosition(float('inf'))
motor2.setVelocity(0.0)

motor3 = robot.getDevice("motor_brazo_3")
sensor3 = robot.getDevice("sensor_brazo_3")
sensor3.enable(timestep)
motor3.setPosition(float('inf'))
motor3.setVelocity(0.0)

motor4 = robot.getDevice("motor_brazo2_3")
sensor4 = robot.getDevice("sensor_brazo2_3")
sensor4.enable(timestep)
motor4.setPosition(float('inf'))
motor4.setVelocity(0.0)

keyboard = Keyboard()
keyboard.enable(timestep)

while robot.step(timestep) != -1:
    key = keyboard.getKey()
    motor1.setVelocity(0.0)
    motor2.setVelocity(0.0)
    motor3.setVelocity(0.0)
    motor4.setVelocity(0.0)
    if key == Keyboard.UP:
        motor1.setVelocity(0.3)
    elif key == Keyboard.DOWN:
        motor1.setVelocity(-0.3)
    elif key == ord('A'):
        motor2.setVelocity(0.3)
    elif key == ord('D'):
        motor2.setVelocity(-0.3)
    elif key == ord('W'):
        motor3.setVelocity(0.3)
    elif key == ord('S'):
        motor3.setVelocity(-0.3)
    elif key == ord('E'):
        motor4.setVelocity(0.3)
    elif key == ord('Q'):
        motor4.setVelocity(-0.3)
