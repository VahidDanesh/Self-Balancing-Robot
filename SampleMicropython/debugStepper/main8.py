from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
from AccelStepper import *

# Configuration
MICROSTEPPING = 3200  # Set this to match the microstepping setting on your TB6600
MAX_SPEED = MICROSTEPPING * 10     # Maximum speed in steps per second
ACCELERATION = MAX_SPEED * 30  # Acceleration in steps per second squared

# Define GPIO pins for Motor 1
STEP_PIN1 = 18  # Connect to PUL+ on TB6600 for Motor 1
DIR_PIN1 = 19   # Connect to DIR+ on TB6600 for Motor 1
ENA_PIN1 = 21   # Connect to ENA+ on TB6600 for Motor 1 (optional)

# Define GPIO pins for Motor 2
STEP_PIN2 = 22  # Connect to PUL+ on TB6600 for Motor 2
DIR_PIN2 = 23   # Connect to DIR+ on TB6600 for Motor 2
ENA_PIN2 = 25   # Connect to ENA+ on TB6600 for Motor 2 (optional)

# NeoPixel for status indication
NEOPIXEL_PIN = 16

# Initialize the stepper motors with DRIVER mode
motor1 = AccelStepper(DRIVER, STEP_PIN1, DIR_PIN1, ENA_PIN1, 0, True)
motor2 = AccelStepper(DRIVER, STEP_PIN2, DIR_PIN2, ENA_PIN2, 0, True)

# Initialize the NeoPixel
np = NeoPixel(Pin(NEOPIXEL_PIN), 1)



def set_neopixel_color(color):
  np[0] = color
  np.write()

def move_motors():
    # Enable the stepper motors
    motor1.enable_outputs()
    motor2.enable_outputs()
    motor1.set_max_speed(MAX_SPEED)
    motor1.set_acceleration(ACCELERATION)
    motor2.set_max_speed(MAX_SPEED)
    motor2.set_acceleration(ACCELERATION)

    while True:
        # Set direction to clockwise for both motors
        set_neopixel_color((0, 255, 0))  # Green for running

        motor1.move_to(MICROSTEPPING * 2)  # Move 2 full revolutions
        motor2.move_to(MICROSTEPPING * 2)  # Move 2 full revolutions


        motor1.run()
        motor2.run()

        # Change direction to counter-clockwise for both motors
        set_neopixel_color((0, 0, 255))  # Blue for changing direction

        motor1.move_to(-MICROSTEPPING * 2)  # Move 2 full revolutions in the opposite direction
        motor2.move_to(-MICROSTEPPING * 2)  # Move 2 full revolutions in the opposite direction


        motor1.run()
        motor2.run()

        # Pause briefly before repeating
        sleep_ms(3000)

try:
  move_motors()

except KeyboardInterrupt:
  # Handle interruption
  set_neopixel_color((255, 0, 0))  # Red for stopped
  motor1.stop()
  motor2.stop()
  motor1.disable_outputs()
  motor2.disable_outputs()
  print("Motor control stopped by user")