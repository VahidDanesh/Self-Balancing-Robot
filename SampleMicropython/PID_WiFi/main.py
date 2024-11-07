import network
import neopixel
import socket
import gc
from web_server import WebServer
from machine import Pin
from config import *


pin = Pin(16, Pin.OUT)
np = neopixel.NeoPixel(pin, 1)

# Function to set NeoPixel color
def set_neopixel_color(r, g, b):
    np[0] = (r, g, b)
    np.write()



# Network Configuration
class NetworkManager:
  def __init__(self):
      self.ssid = NETWORK['ssid']
      self.password = NETWORK['password']
      self.ap = network.WLAN(network.AP_IF)

  def start_ap(self):
      """Start Access Point"""
      self.ap.active(True)
      self.ap.config(essid=self.ssid, 
                    password=self.password,
                    authmode=NETWORK['authmode'])
      
      while not self.ap.active():
          pass
      
      print('\n=== WiFi Access Point Created ===')
      print('To connect to the robot:')
      print(f'1. Connect to WiFi network: "{self.ssid}"')
      print(f'2. Use password: "{self.password}"')
      print(f'3. Open browser and go to: http://{self.ap.ifconfig()[0]}')
      print('================================\n')
      set_neopixel_color(0, 0, 50)
      return self.ap

class RobotController:
  def __init__(self):
      """Initialize robot controller with default values"""
      self.pid_values = {
          key: PID[key]['default'] for key in PID
      }
      self.current_mode = MODES['default']
      self.current_speed = MOTOR['default_speed']

  def handle_command(self, cmd):
      """Handle movement commands"""
      if cmd == 'accelerate':
          self.current_speed = min(
              self.current_speed + MOTOR['acceleration_step'],
              MOTOR['max_speed']
          )
      elif cmd == 'decelerate':
          self.current_speed = max(
              self.current_speed - MOTOR['acceleration_step'],
              MOTOR['min_speed']
          )

  def update_pid(self, new_values):
      """Update PID values"""
      print(f"Updating PID values: {new_values}")
      for key in new_values:
          if key in self.pid_values:
              self.pid_values[key] = float(new_values[key])

  def set_mode(self, mode):
      """Set operation mode"""
      print(f"Changing mode to: {mode}")
      self.current_mode = mode



def check_system_status():
  """Print system status for debugging"""
  import os
  
  print("\n=== System Status ===")
  
  # Check files
  print("\nFiles on system:")
  files = os.listdir()
  required_files = ['main.py', 'config.py', 'web_server.py', 'index.html', 'config.js']
  for file in required_files:
      status = "OK" if file in files else "NOT FOUND"
      print(f"{status} {file}")
  
  # Check memory
  import gc
  gc.collect()
  print(f"\nFree memory: {gc.mem_free()} bytes")
  
  # Check network
  import network
  ap = network.WLAN(network.AP_IF)
  print("\nNetwork status:")
  print(f"Active: {ap.active()}")
  if ap.active():
      print(f"Network: {ap.config('essid')}")
      print(f"IP Address: {ap.ifconfig()[0]}")





def main():


    write_js_config()
       # Add this to main.py after write_js_config()
    import os
    print("\nChecking files:")
    print(os.listdir())  # This will show all files on ESP32

    # check whether the 'config.js' file is created
    if 'config.js' in os.listdir():
        print("config.js file created successfully!")
    else:
        print("Error creating config.js file!")
        set_neopixel_color(100, 0, 0)

    # Initialize components
    network_manager = NetworkManager()
    web_server = WebServer()
    robot = RobotController()

    # Register handlers
    web_server.register_handler('command', robot.handle_command)
    web_server.register_handler('pid', robot.update_pid)
    web_server.register_handler('mode', robot.set_mode)

    # Start access point
    network_manager.start_ap()

    # Start web server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', SERVER['port']))
    s.listen(SERVER['max_connections'])
    print('Web server started. Listening for incoming connections...')

    # Main server loop
    while True:
        try:
            gc.collect()  # Clean up memory
            conn, addr = s.accept()
            print('Client connected from:', addr)
            request = conn.recv(1024).decode()
            
            response = web_server.parse_request(request)
            conn.send(response.encode('utf-8'))
            set_neopixel_color(0, 100, 0)
            conn.close()
            
        except Exception as e:
            print('Error:', e)
            set_neopixel_color(100, 0, 0)
            try:
                conn.close()
            except:
                pass

if __name__ == '__main__':
    try:
        check_system_status()
        main()
    except KeyboardInterrupt:
        print('Server stopped')
        set_neopixel_color(255, 0, 0)
