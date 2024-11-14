from machine import Pin
import time
import neopixel




# Define the GPIO pins for PUL, DIR, and ENA
pul_pin = Pin(18, Pin.OUT)
dir_pin = Pin(19, Pin.OUT)
ena_pin = Pin(21, Pin.OUT)

neo_pin = Pin(16, Pin.OUT)
neo = neopixel.NeoPixel(neo_pin, 1)

def neopixel_color(r, g, b):
    neo[0] = (r, g, b)
    neo.write()

# Function to control the stepper motor
def stepper_motor_control(steps, delay, direction):
  # Set the direction
  dir_pin.value(direction)
  
  # Enable the motor
  ena_pin.value(0)  # Assuming active low enable
  
  for _ in range(steps):
      pul_pin.on()
      neopixel_color(0, 100, 0)
      time.sleep(delay)
      pul_pin.off()
      time.sleep(delay)
      neopixel_color(0, 0, 100)
  
  # Disable the motor
  ena_pin.value(1)  # Assuming active low enable

# Main loop
try:
  while True:
      # Rotate the motor 200 steps forward
      stepper_motor_control(200, 0.001, 1)
      time.sleep(1)
      
      # Rotate the motor 200 steps backward
      stepper_motor_control(200, 0.001, 0)
      time.sleep(1)

except KeyboardInterrupt:
  print("Motor control stopped")
  neopixel_color(100, 0, 0)