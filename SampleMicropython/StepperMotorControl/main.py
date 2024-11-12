from machine import Pin, Timer
import time
import neopixel

# NeoPixel setup
pin = Pin(16, Pin.OUT)
np = neopixel.NeoPixel(pin, 1)

# Function to set NeoPixel color
def set_neopixel_color(r, g, b):
    np[0] = (r, g, b)
    np.write()



# Define GPIO pins
DIR_PIN = 18
PUL_PIN = 19
ENA_PIN = 21
LED_PIN = 2  # Built-in LED on most ESP32 boards

# Initialize pins
dir_pin = Pin(DIR_PIN, Pin.OUT)
pul_pin = Pin(PUL_PIN, Pin.OUT)
ena_pin = Pin(ENA_PIN, Pin.OUT)
led = Pin(LED_PIN, Pin.OUT)

# Enable the motor driver
ena_pin.value(0)  # Active low to enable

# Function to step the motor
def step_motor(steps, direction, speed):
    dir_pin.value(direction)
    delay = 1.0 / speed  # Calculate delay based on speed

    for _ in range(steps):
        pul_pin.value(1)
        time.sleep(delay / 2)
        pul_pin.value(0)
        time.sleep(delay / 2)

# Main loop
try:
    while True:
        # Rotate 180 degrees (assuming 200 steps per revolution)
        led.value(1)  # Turn on LED
        set_neopixel_color(0, 100, 0)
        step_motor(100, 1, 100)  # 100 steps, forward, 100 steps per second
        led.value(0)  # Turn off LED
        time.sleep(2)  # Wait for 2 seconds

        # Change speed and direction
        led.value(1)  # Turn on LED
        step_motor(100, 0, 200)  # 100 steps, backward, 200 steps per second
        set_neopixel_color(0, 0, 100)
        led.value(0)  # Turn off LED
        time.sleep(2)  # Wait for 2 seconds

except KeyboardInterrupt:
    # Handle any cleanup here if necessary
    led.value(0)  # Ensure LED is off
    ena_pin.value(1)  # Disable the motor driver
    set_neopixel_color(100, 0, 0) 
