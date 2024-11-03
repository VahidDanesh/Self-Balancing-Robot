import bluetooth
import neopixel
import machine
import time
from ble_advertising import advertising_payload
from micropython import const

# Constants for BLE events
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# Flags for BLE characteristics
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# UUIDs for UART service and characteristics
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

class BLESimplePeripheral:
    def __init__(self, ble, name="ESP32"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()   
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            print("The BLE connection is successful.")
            self._connections.add(conn_handle)
            led.value(0)  # Turn off status LED when connected
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            led.value(1)  # Turn on status LED when disconnected
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback

def demo():
    # Initialize NeoPixel
    np_pin = machine.Pin(16, machine.Pin.OUT)  # Use GPIO 16 for NeoPixel
    np = neopixel.NeoPixel(np_pin, 1)  # One NeoPixel

    # Initialize status LED
    global led
    led = machine.Pin(2, machine.Pin.OUT)  # Use GPIO 2 for status LED

    # Turn on status LED initially (indicating no connection)
    led.value(1)

    # Initialize BLE
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(rx_data):
        print("RX", rx_data)
        # Expecting RGB values in the format "R,G,B"
        try:
            r, g, b = map(int, rx_data.decode("utf-8").strip().split(","))
            np[0] = (r, g, b)  # Set NeoPixel color
            np.write()
            led.value(0)  # Turn off LED when receiving data

            
        except Exception as e:
            print("Error parsing RGB data:", e)

    p.on_write(on_rx)

    print("Please use a BLE scanning app to connect to the ESP32.")

    while True:
        if p.is_connected():
            # Turn on the NeoPixel when connected
            
            np.write()
        else:
            led.value(1)  # Keep status LED on while not connected
            np[0] = (255, 255, 255)  # Set NeoPixel to white as an example
        time.sleep(1)

if __name__ == "__main__":
    demo()
