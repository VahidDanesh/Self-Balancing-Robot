# Self-Balancing-Robot

## ESP32 Projects with MicroPython

This document outlines the installation process for setting up an ESP32 board with MicroPython, along with brief explanations of three projects: blinking an LED, controlling a NeoPixel LED, and using Bluetooth communication.

## Table of Contents
1. [Installation Process](#installation-process)
2. [Project Descriptions](#project-descriptions)
   - [Blinking an LED](#blinking-an-led)
   - [Controlling a NeoPixel LED](#controlling-a-neopixel-led)
   - [Bluetooth Communication](#bluetooth-communication)

## Installation Process

### Step 1: Install Required Software

1. **Install Python**:
   - Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).

2. **Install `esptool`**:
   - Open a terminal and run the following command:
     ```bash
     pip install esptool
     ```

3. **Install MicroPython Firmware**:
   - Download the latest MicroPython firmware for the ESP32 from the [MicroPython downloads page](https://micropython.org/download/esp32/).

### Step 2: Connect ESP32 to Your Computer

- Connect the ESP32 board to your computer using a USB cable.

### Step 3: Identify the Serial Port

- Use the command below to find the correct serial port:
  ```bash
  ls /dev/tty*
  ```

### Step 4: Erase Flash Memory (Optional)

- It's a good practice to erase the flash memory before flashing new firmware:
  ```bash
  esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
  ```

### Step 5: Flash MicroPython Firmware

- Flash the MicroPython firmware to the ESP32:
  ```bash
  esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-xxxxxx.bin
  ```

### Step 6: Access the REPL

- You can access the MicroPython REPL using a terminal program like `screen`, `picocom`, or an IDE like Thonny.

```bash
screen /dev/ttyUSB0 115200
```

## Project Descriptions

### Blinking an LED

In this project, we will blink an LED connected to a GPIO pin of the ESP32. This serves as a basic introduction to controlling GPIO pins.

**Code Example**:
```python
from machine import Pin
import time

led = Pin(2, Pin.OUT)

while True:
    led.on()  # Turn LED on
    time.sleep(1)  # Wait for 1 second
    led.off()  # Turn LED off
    time.sleep(1)  # Wait for 1 second
```

### Controlling a NeoPixel LED

This project demonstrates how to control a NeoPixel LED strip using the ESP32. NeoPixels can be programmed to display various colors and patterns.

**Code Example**:
```python
import machine
import neopixel

pin = machine.Pin(16, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, 1)  # 1 NeoPixel

while True:
    np[0] = (255, 0, 0)  # Red
    np.write()
    time.sleep(1)
    np[0] = (0, 255, 0)  # Green
    np.write()
    time.sleep(1)
    np[0] = (0, 0, 255)  # Blue
    np.write()
    time.sleep(1)
```

### Bluetooth Communication

This project enables Bluetooth communication between the ESP32 and a smartphone. The ESP32 acts as a Bluetooth peripheral, allowing the phone to send commands to it.

**Code Example**:
```python
import bluetooth
from ble_advertising import advertising_payload
import machine

# BLE configuration here...

# Functionality to receive data and control an LED based on connection state

while True:
    if p.is_connected():
        # Perform actions when connected
    else:
        # Blink an LED when not connected
```

## Conclusion

These projects provide a foundational understanding of using the ESP32 with MicroPython. You can expand on these projects by adding features or integrating additional components. 

Feel free to explore and modify the code to suit your needs!