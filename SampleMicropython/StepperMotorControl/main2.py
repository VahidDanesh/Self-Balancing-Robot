try:
  from stepper import Stepper
  print("Stepper module imported successfully")
except ImportError as e:
  print("Error importing stepper module:", e)
from machine import Pin
import time
import neopixel




# Define GPIO pins
DIR_PIN = 18
PUL_PIN = 19
ENA_PIN = 21
LED_PIN = 2  # Built-in LED on most ESP32 boards

# NeoPixel setup
pin = Pin(16, Pin.OUT)
np = neopixel.NeoPixel(pin, 1)

# Function to set NeoPixel color
def set_neopixel_color(r, g, b):
    np[0] = (r, g, b)
    np.write()


# Initialize the stepper motor
stepper = Stepper(PUL_PIN, DIR_PIN, steps_per_rev=200, speed_sps=500)

# Initialize the LED
led = Pin(LED_PIN, Pin.OUT)

# Function to run the motor and control the LED
def run_motor():
  # Rotate in one direction
  stepper.target_deg(180)
  print("Rotating 180 degrees")
  led.value(1)  # Turn on LED
  set_neopixel_color(0, 100, 0)  # Set NeoPixel color to green

  time.sleep(3)  # Wait for the motor to reach the target position

  # Stop for 2 seconds
  led.value(0)  # Turn off LED
  set_neopixel_color(0, 0, 0)  # Set NeoPixel color to off
  time.sleep(2)

  # Change speed
  stepper.speed(200)  # Change speed to 200 steps per second
  print("Changing speed to 200 steps per second")

  # Rotate in the opposite direction
  stepper.target_deg(0)
  print("Rotating back to 0 degrees")
  led.value(1)  # Turn on LED
  set_neopixel_color(0, 0, 100)  # Set NeoPixel color to red
  time.sleep(3)  # Wait for the motor to reach the target position

  # Stop for 2 seconds
  led.value(0)  # Turn off LED
  time.sleep(2)

# Main loop
try:
  while True:
      run_motor()

except KeyboardInterrupt:
  # Handle any cleanup here if necessary
  led.value(0)  # Ensure LED is off
  stepper.stop()  # Stop the motor
  set_neopixel_color(100, 0, 0)  
  print("Program stopped by user")