import wifimgr
from time import sleep
import machine
from machine import Pin
import neopixel

pin = Pin(16, Pin.OUT)
np = neopixel.NeoPixel(pin, 1)

def set_neopixel_color(r, g, b):
  np[0] = (r, g, b)
  np.write()

try:
  import usocket as socket
except:
  import socket

led = machine.Pin(2, machine.Pin.OUT)

wlan = wifimgr.get_connection()

if wlan is None:
  print("Could not initialize the network connection.")
  set_neopixel_color(255, 0, 0)
  while True:
      pass

print("ESP OK")

def read_html_file():
  with open('index.html', 'r') as file:
      return file.read()

try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('', 80))
  s.listen(5)
  set_neopixel_color(0, 255, 0)
except OSError as e:
  machine.reset()

while True:
  try:
      conn, addr = s.accept()
      conn.settimeout(3.0)
      print('Got a connection from %s' % str(addr))
      request = conn.recv(1024)
      conn.settimeout(None)
      request = str(request)
      print('Content = %s' % request)
      
      led_on = request.find('/?led=on')
      led_off = request.find('/?led=off')
      color_change = request.find('/?color=')
      
      if led_on == 6:
          print('LED ON')
          led.value(1)
      if led_off == 6:
          print('LED OFF')
          led.value(0)
      if color_change == 6:
          color_value = request.split('=')[1][:6]
          r = int(color_value[0:2], 16)
          g = int(color_value[2:4], 16)
          b = int(color_value[4:6], 16)
          set_neopixel_color(r, g, b)
          print(f'Color changed to RGB({r}, {g}, {b})')
      
      response = read_html_file()
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      conn.close()
  except OSError as e:
      conn.close()
      print('Connection closed')