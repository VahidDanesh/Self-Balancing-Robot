from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms, ticks_ms
import AccelStepper
from AccelStepper import AccelStepper

# Configuration
MICROSTEPPING = 800  # Set this to match the microstepping setting on your TB6600
MAX_SPEED = 2000     # Maximum speed in steps per second
ACCELERATION = 1000  # Acceleration in steps per second squared
RUN_DURATION = 5000  # Duration to run in the opposite direction in milliseconds

# Define GPIO pins
STEP_PIN = 18  # Connect to PUL+ on TB6600
DIR_PIN = 19   # Connect to DIR+ on TB6600
ENA_PIN = 21   # Connect to ENA+ on TB6600 (optional, can be tied to VCC if always enabled)
NEOPIXEL_PIN = 16
DRIVER = 1


# Initialize the stepper motor with DRIVER mode
stepper_motor = AccelStepper(DRIVER, STEP_PIN, DIR_PIN, ENA_PIN, 0, True)

# Initialize the NeoPixel
np = NeoPixel(Pin(NEOPIXEL_PIN), 1)

def set_neopixel_color(color):
    np[0] = color
    np.write()

def move_motor():
    # Enable the stepper motor
    stepper_motor.enable_outputs()
    stepper_motor.set_max_speed(MAX_SPEED)
    stepper_motor.set_acceleration(ACCELERATION)

    while True:
        # Move the motor in one direction
        set_neopixel_color((0, 255, 0))  # Green for running
        stepper_motor.move_to(MICROSTEPPING * 2)  # Move 2 full revolutions
        while stepper_motor.run():
            pass

        # Change speed and move in the opposite direction for a set duration
        set_neopixel_color((0, 0, 255))  # Blue for changing direction
        stepper_motor.set_speed(-MAX_SPEED / 2)  # Set speed for reverse direction
        start_time = ticks_ms()
        while ticks_ms() - start_time < RUN_DURATION:
            stepper_motor.run_speed()

try:
    move_motor()

except KeyboardInterrupt:
    # Handle interruption
    set_neopixel_color((255, 0, 0))  # Red for stopped
    stepper_motor.stop()
    stepper_motor.disable_outputs()
    print("Motor control stopped by user")