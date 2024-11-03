import network
import socket
from machine import Pin
import neopixel
import time

# Valid configuration for Wi-Fi AP
ssidAP = 'ESP32_AP'
passwordAP = '12345678'
local_IP = '192.168.4.1'  # Updated IP to 192.168.4.1
gateway = '192.168.4.1'   # Gateway should be the same as the local IP for AP mode
subnet = '255.255.255.0'  # Standard subnet mask

# NeoPixel setup
pin = Pin(16, Pin.OUT)
np = neopixel.NeoPixel(pin, 1)

# Function to set NeoPixel color
def set_neopixel_color(r, g, b):
    np[0] = (r, g, b)
    np.write()

# Set initial color to off
set_neopixel_color(0, 0, 0)

# Access Point Setup
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssidAP, authmode=network.AUTH_WPA_WPA2_PSK, password=passwordAP)

# Set the AP IP configuration properly to avoid DHCP issues
ap.ifconfig([local_IP, gateway, subnet, gateway])
ap.active(True)
print("AP Setup Complete. IP Address:", ap.ifconfig())

# Web Server setup
def web_page():
    html = """<html>
                <head><title>ESP32 LED Control</title></head>
                <body>
                    <h1>ESP32 LED Control</h1>
                    <form action="/?color=red" method="get"><button>Red</button></form>
                    <form action="/?color=green" method="get"><button>Green</button></form>
                    <form action="/?color=blue" method="get"><button>Blue</button></form>
                    <form action="/?color=off" method="get"><button>Off</button></form>
                </body>
              </html>"""
    return html

# Function to handle incoming requests
def handle_requests():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print("Listening for incoming connections...")

    while True:
        
        set_neopixel_color(255, 255, 0)
        conn, addr = s.accept()
        print("Connection from", addr)
        request = conn.recv(1024)
        request = str(request)
        print("Request:", request)

        # Check for color command
        if '/?color=red' in request:
            set_neopixel_color(255, 0, 0)
        elif '/?color=green' in request:
            set_neopixel_color(0, 255, 0)
        elif '/?color=blue' in request:
            set_neopixel_color(0, 0, 255)
        elif '/?color=off' in request:
            set_neopixel_color(0, 0, 0)

        # Respond with HTML page
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

# Run the AP setup and web server
try:
    handle_requests()
except KeyboardInterrupt:
    ap.active(False)
    print("Server stopped and AP deactivated.")
