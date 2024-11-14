import machine
import time
from stepper import Stepper
from neopixel import NeoPixel

# Define GPIO pins
pul_pin = 18
dir_pin = 19
ena_pin = 21
neopixel_pin = 16

# Initialize the stepper motor
stepper_motor = Stepper(pul_pin, dir_pin, ena_pin, steps_per_rev=200, speed_sps=100)

# Initialize the NeoPixel
np = NeoPixel(machine.Pin(neopixel_pin), 1)

def set_neopixel_color(color):
    np[0] = color
    np.write()

try:
    # Enable the stepper motor active low
    stepper_motor.enable(0)
    print(stepper_motor.is_enabled())
    
    while True:
        # Set NeoPixel to green when running
        set_neopixel_color((0, 255, 0))
        
        # Move the motor 400 steps forward
        stepper_motor.target(400)
        time.sleep(2)
        
        # Set NeoPixel to blue when idle
        set_neopixel_color((0, 0, 255))
        time.sleep(1)
        
        # Set NeoPixel to green when running
        set_neopixel_color((0, 255, 0))
        # Move the motor 400 steps backward
        stepper_motor.target(-400)
        time.sleep(2)
        
        # Set NeoPixel to blue when idle
        set_neopixel_color((0, 0, 255))
        time.sleep(1)

except KeyboardInterrupt:
    # Set NeoPixel to red when stopped
    set_neopixel_color((255, 0, 0))
    stepper_motor.stop()
    print("Motor control stopped")
