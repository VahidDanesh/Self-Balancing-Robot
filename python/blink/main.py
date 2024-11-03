import machine
import time


# Set up pin 2 as an output pin
led = machine.Pin(2, machine.Pin.OUT)

# Blink the LED in a loop
while True:
    led.on()      # Turn LED on
    time.sleep(0.05) # Wait 1 second
    led.off()     # Turn LED off
    time.sleep(0.05) # Wait 1 second

