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

keyboard = Keyboard()
keyboard.enable(timestep)

while robot.step(timestep) != -1:
    key = keyboard.getKey()
    if key == Keyboard.UP:
        motor1.setVelocity(0.3)
        motor2.setVelocity(0.0)
    elif key == Keyboard.DOWN:
        motor1.setVelocity(-0.3)
        motor2.setVelocity(0.0)
    elif key == ord('A'):
        motor2.setVelocity(0.3)
        motor1.setVelocity(0.0)
    elif key == ord('D'):
        motor2.setVelocity(-0.3)
        motor1.setVelocity(0.0)
    else:
        motor1.setVelocity(0.0)
        motor2.setVelocity(0.0)
