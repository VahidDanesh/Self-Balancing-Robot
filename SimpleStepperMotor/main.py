import machine
import time
from stepper import Stepper
from neopixel import NeoPixel

# Define GPIO pins
pul_pin = 18
dir_pin = 19
ena_pin = 21
neopixel_pin = 16
steps = 3200
speed = steps * 10
# Initialize the stepper motor with enable active low
stepper_motor = Stepper(pul_pin, dir_pin, ena_pin, steps_per_rev=steps, speed_sps=speed, en_active_low=True)
stepper_motor.speed_rps(10)
# Initialize the NeoPixel
np = NeoPixel(machine.Pin(neopixel_pin), 1)

def set_neopixel_color(color):
  np[0] = color
  np.write()

try:
  # Enable the stepper motor (active low logic)
  stepper_motor.enable(1)  # Enable the motor (active low means setting to 1 will disable, so we use 1 to enable)
  print(stepper_motor.is_enabled())
  
  while True:
      # Set NeoPixel to green when running
      set_neopixel_color((0, 255, 0))
      
      stepper_motor.target_deg(360*10)
      time.sleep(2)
      
      # Set NeoPixel to blue when idle
      set_neopixel_color((0, 0, 255))
      time.sleep(1)
      
      # Set NeoPixel to green when running
      set_neopixel_color((0, 255, 0))
      
      stepper_motor.target_deg(-360*10)
      time.sleep(2)
      
      # Set NeoPixel to blue when idle
      set_neopixel_color((0, 0, 255))
      time.sleep(1)

except KeyboardInterrupt:
  # Set NeoPixel to red when stopped
  set_neopixel_color((255, 0, 0))
  stepper_motor.stop()
  print("Motor control stopped")