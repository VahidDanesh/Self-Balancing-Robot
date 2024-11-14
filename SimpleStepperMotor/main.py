from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms, ticks_ms
from AccelStepper import *

# Configuration
MAX_SPEED = 2000000  # Maximum speed in steps per second
RUN_DURATION = 10000  # Duration to run in each direction in milliseconds

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

def run_motors_for_duration(duration_ms, speed):
  start_time = ticks_ms()
  while ticks_ms() - start_time < duration_ms:
      motor1.run_speed()
      motor2.run_speed()

def move_motors():
  # Enable the stepper motors
  motor1.enable_outputs()
  motor2.enable_outputs()
  motor1.set_max_speed(MAX_SPEED)
  motor2.set_max_speed(MAX_SPEED)
  

  while True:
      # Set direction to clockwise for both motors
      set_neopixel_color((0, 255, 0))  # Green for running


      print("Motor 1 Speed: ", motor1.speed())
      print("Motor 2 Speed: ", motor2.speed())


      motor1.set_speed(MAX_SPEED)
      motor2.set_speed(MAX_SPEED)

      print("Motor 1 Speed: ", motor1.speed())
      print("Motor 2 Speed: ", motor2.speed())
      
      run_motors_for_duration(RUN_DURATION, MAX_SPEED)

      # Change direction to counter-clockwise for both motors
      set_neopixel_color((0, 0, 255))  # Blue for changing direction

      motor1.set_speed(-MAX_SPEED)
      motor2.set_speed(-MAX_SPEED)
      run_motors_for_duration(RUN_DURATION, -MAX_SPEED)

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