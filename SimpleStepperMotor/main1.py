import machine
from machine import Pin
from neopixel import NeoPixel
import time
from mystepper import Stepper

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

def print_status(stepper, message=""):
    """Print current status of the stepper motor"""
    print(f"\n--- {message} ---")
    print(f"Position: {stepper.get_position()} steps ({stepper.get_position_deg():.2f}°) with target {stepper.target_pos} steps")
    print(f"Speed: {stepper.get_speed():.2f} steps/sec ({stepper.sps2rpm(stepper.get_speed()):.2f} RPM)")
    print(f"Running: {stepper.is_running()}")

def test_basic_movement(stepper):
    """Test basic movement with acceleration"""
    print("\n=== Testing Basic Movement ===")
    
    # Move 400 steps forward
    print("\nMoving 400 steps forward...")
    set_neopixel_color(COLOR_MOVING)
    stepper.move_to_deg(360)
    
    # Wait until movement completes while monitoring status
    while stepper.is_running():
        print_status(stepper, "Moving forward")
        time.sleep(1)
    
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Movement completed")
    time.sleep(1)
    
    # Move back to zero
    print("\nMoving back to zero...")
    set_neopixel_color(COLOR_MOVING)
    stepper.move_to(0)
    
    while stepper.is_running():
        print_status(stepper, "Moving to zero")
        time.sleep(1)
    
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Returned to zero")

def test_free_run(stepper):
    """Test free running mode"""
    print("\n=== Testing Free Run Mode ===")
    
    # Run forward for 3 seconds
    print("\nFree running forward...")
    set_neopixel_color(COLOR_FREE_RUNNING)
    stepper.free_run(1, 800)  # Run forward at 800 steps/sec
    
    start_time = time.time()
    while time.time() - start_time < 3:
        print_status(stepper, "Free running forward")
        time.sleep(1)
    
    # Run reverse for 3 seconds
    print("\nFree running reverse...")
    stepper.free_run(-1, 400)  # Run reverse at 400 steps/sec
    
    start_time = time.time()
    while time.time() - start_time < 3:
        print_status(stepper, "Free running reverse")
        time.sleep(1)
    
    # Stop free run
    print("\nStopping free run...")
    stepper.free_run(0)
    set_neopixel_color(COLOR_IDLE)
    print_status(stepper, "Free run stopped")

def test_acceleration_profiles(stepper):
    """Test different acceleration profiles"""
    print("\n=== Testing Acceleration Profiles ===")
    
    # Test high acceleration
    stepper.set_acceleration(2000)
    print("\nMoving with high acceleration (2000 steps/s²)...")
    set_neopixel_color(COLOR_ACCELERATING)
    stepper.move(800)
    
    while stepper.is_running():
        print_status(stepper, "High acceleration movement")
        time.sleep(1)
    
    time.sleep(1)
    
    # Test low acceleration
    stepper.set_acceleration(200)
    print("\nMoving with low acceleration (200 steps/s²)...")
    set_neopixel_color(COLOR_ACCELERATING)
    stepper.move(-800)
    
    while stepper.is_running():
        print_status(stepper, "Low acceleration movement")
        time.sleep(0.1)
    
    set_neopixel_color(COLOR_IDLE)

def test_emergency_stop(stepper):
    """Test emergency stop functionality"""
    print("\n=== Testing Emergency Stop ===")
    
    # Start a long movement
    print("\nStarting long movement...")
    set_neopixel_color(COLOR_MOVING)
    stepper.move(2000)
    
    # Wait a bit then trigger emergency stop
    time.sleep(1)
    print("\nTriggering emergency stop!")
    set_neopixel_color(COLOR_EMERGENCY)
    stepper.emergency_stop()
    
    print_status(stepper, "After emergency stop")
    time.sleep(1)
    set_neopixel_color(COLOR_IDLE)

try:
        # Initialize stepper with moderate speed and acceleration
    stepper = Stepper(
        step_pin=STEP_PIN,
        dir_pin=DIR_PIN,
        en_pin=EN_PIN,
        steps_per_rev=3200,
        speed_sps=6000*2,
        max_speed_sps=6000*3,
        acceleration=6000*10,
        timer_id=0,
        en_active_low=True
    )
except Exception as e:
    print(f"Error initializing stepper: {e}")
    set_neopixel_color(COLOR_EMERGENCY)
    raise



def main():
    """Main test sequence"""
    try:
        
        print("\nStepper motor initialized")
        print(f"Max speed: {stepper.get_max_speed()} steps/sec")
        print(f"Acceleration: {stepper.get_acceleration()} steps/sec²")
        
        # Enable the motor
        stepper.enable(True)
        set_neopixel_color(COLOR_IDLE)
        
        # Run all tests
        test_basic_movement(stepper)
        time.sleep(1)
        
        test_free_run(stepper)
        time.sleep(1)
        
        test_acceleration_profiles(stepper)
        time.sleep(1)
        
        test_emergency_stop(stepper)
        
        # Cleanup
        stepper.enable(False)
        set_neopixel_color(COLOR_IDLE)
        print("\nTest sequence completed")
        
    except Exception as e:
        set_neopixel_color(COLOR_EMERGENCY)
        print(f"Error occurred: {e}")
        stepper.stop()
        stepper.enable(False)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Stopped Script {e}")
        stepper.stop()
        set_neopixel_color(COLOR_EMERGENCY)
        raise
