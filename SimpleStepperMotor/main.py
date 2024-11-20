import machine
import time
from neopixel import NeoPixel
from stepper import Stepper


# Initialize the NeoPixel
NEOPIXEL_PIN = 16
np = NeoPixel(machine.Pin(NEOPIXEL_PIN), 1)

# Colors for different states (RGB format)
COLOR_IDLE = (0, 0, 0)        # Off
COLOR_MOVING = (0, 255, 0)    # Green
COLOR_ACCELERATING = (0, 0, 255)  # Blue
COLOR_DECELERATING = (255, 165, 0)  # Orange
COLOR_FREE_RUNNING = (255, 0, 255)  # Purple
COLOR_EMERGENCY = (255, 0, 0)  # Red

def set_neopixel_color(color):
  np[0] = color
  np.write()

# Initialize stepper motor
STEP_PIN = 18
DIR_PIN = 19
EN_PIN = 21

stepper = Stepper(step_pin=STEP_PIN, dir_pin=DIR_PIN, en_pin=EN_PIN, 
                steps_per_rev=1600, speed_sps=1600*5, invert_dir=False, 
                timer_id=0, en_active_low=True)

def print_status(stepper, message=""):
  """Print current status of the stepper motor"""
  print(f"\n--- {message} ---")
  print(f"Position: {stepper.get_pos()} steps ({stepper.get_pos_deg():.2f}°) with target {stepper.target_pos} steps")
  print(f"Speed: {stepper.steps_per_sec:.2f} steps/sec")
  print(f"Running: {stepper.timer_is_running}")

# Enable the stepper motor
stepper.enable(True)
set_neopixel_color(COLOR_IDLE)
print_status(stepper, "Motor Initialized")


# Free run the motor in a positive direction
stepper.free_run(1)
set_neopixel_color(COLOR_FREE_RUNNING)
print_status(stepper, "Free Running")


# run for 20 second and print status each 1 seconds
# do not use time.sleep() in the loop
start_time = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), start_time) < 20000:
  if time.ticks_diff(time.ticks_ms(), start_time) % 1000 == 0:
    
    print_status(stepper)
  
  



# Stop the motor
stepper.stop()
set_neopixel_color(COLOR_IDLE)
print_status(stepper, "Stopped Free Running")

# Disable the stepper motor
stepper.enable(False)
set_neopixel_color(COLOR_IDLE)
print_status(stepper, "Motor Disabled")