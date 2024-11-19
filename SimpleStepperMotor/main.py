import machine
import time
from mystepper import Stepper
from neopixel import NeoPixel

# Define GPIO pins
pul_pin = 18
dir_pin = 19
ena_pin = 21
neopixel_pin = 16
steps = 3200
speed = steps * 2
a = speed * 2
# Initialize the stepper motor with enable active low
stepper_motor = Stepper(pul_pin, dir_pin, ena_pin, steps_per_rev=steps, 
                        max_speed_sps=speed, acceleration=a, en_active_low=True)

newspeed = stepper_motor.rpm2sps(400)
print("sps for 300 rpm", newspeed)

stepper_motor.set_max_speed(newspeed)
stepper_motor.set_acceleration(stepper_motor.rpm2sps(50))

# Initialize the NeoPixel
np = NeoPixel(machine.Pin(neopixel_pin), 1)

def set_neopixel_color(color):
  np[0] = color
  np.write()

try:
  # Enable the stepper motor (active low logic)
  stepper_motor.enable(1)  # Enable the motor (active low means setting to 1 will disable, so we use 1 to enable)
  
  
  while True:
      # Set NeoPixel to green when running
      set_neopixel_color((0, 255, 0))
      
      stepper_motor.move_to_deg(360*3)
      print(stepper_motor.get_speed())


      
      time.sleep(5)
      
      
      
      # Set NeoPixel to blue when idle
      set_neopixel_color((0, 0, 255))
      time.sleep(1)
      
      # Set NeoPixel to green when running
      set_neopixel_color((0, 255, 0))
      
      stepper_motor.move_to_deg(-360*3)

      time.sleep(5)

      
     

      # Set NeoPixel to blue when idle
      set_neopixel_color((0, 0, 255))
      time.sleep(1)

except KeyboardInterrupt:
  # Set NeoPixel to red when stopped
  set_neopixel_color((255, 0, 0))
  stepper_motor.stop()
  print("Motor control stopped")