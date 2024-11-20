import machine
from machine import Pin
from neopixel import NeoPixel
import time
from cubicStepper import Stepper

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
                  steps_per_rev=3200, speed_sps=3200, invert_dir=False, 
                  timer_id=0, en_active_low=True, accel_time=0.5)

def print_status(stepper, message=""):
    """Print current status of the stepper motor"""
    print(f"\n--- {message} ---")
    print(f"Position: {stepper.get_pos()} steps ({stepper.get_pos_deg():.2f}°) with target {stepper.target_pos} steps")
    print(f"Speed: {stepper.get_speed():.2f} steps/sec")
    print(f"Running: {stepper.timer_is_running}")

def main():
    # Enable the stepper motor
    stepper.enable(True)
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Initialized")

    # Set a target position
    target_deg = 360 * 3  # Move 400 steps
    stepper.target_deg(target_deg)
    set_neopixel_color(COLOR_ACCELERATING)
    print_status(stepper, "Starting Movement")

    # Start moving towards the target
    while stepper.get_pos_deg() != target_deg:
        time.sleep(1)
        print_status(stepper, "Moving")
        set_neopixel_color(COLOR_MOVING)

    # Once the target is reached, stop the motor
    stepper.stop()
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Target Reached")

    # Free run demonstration
    stepper.free_run(1)  # Start free running
    set_neopixel_color(COLOR_FREE_RUNNING)
    time.sleep(2)  # Run for 2 seconds
    stepper.stop()
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Free Run Stopped")

    # Disable the stepper motor
    stepper.enable(False)
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Disabled")

if __name__ == "__main__":
    main()