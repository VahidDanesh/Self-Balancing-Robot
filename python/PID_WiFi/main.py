import network
import socket
import gc
from web_server import WebServer

# Network Configuration
class NetworkManager:
  def __init__(self, ssid="RobotControl", password="robot123"):
      self.ssid = ssid
      self.password = password
      self.ap = network.WLAN(network.AP_IF)

  def start_ap(self):
      """Start Access Point"""
      self.ap.active(True)
      self.ap.config(essid=self.ssid, 
                    password=self.password,
                    authmode=network.AUTH_WPA_WPA2_PSK)
      
      while not self.ap.active():
          pass
      
      print('Access Point Created')
      print('Network Name:', self.ssid)
      print('Password:', self.password)
      print('IP Address:', self.ap.ifconfig()[0])
      return self.ap

class RobotController:
  def __init__(self):
      """Initialize robot controller with default values"""
      self.pid_values = {
          'kp': 1.00,
          'ki': 0.50,
          'kd': 0.25
      }
      self.current_mode = 'balance'
      self.current_speed = 0

  def handle_command(self, cmd):
      """Handle movement commands"""
      print(f"Command received: {cmd}")
      # Add motor control implementation here when needed

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

def main():
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
  s.bind(('', 80))
  s.listen(5)
  print('Web server started')

  # Main server loop
  while True:
      try:
          gc.collect()  # Clean up memory
          conn, addr = s.accept()
          print('Client connected from:', addr)
          request = conn.recv(1024).decode()
          
          response = web_server.parse_request(request)
          conn.send(response.encode('utf-8'))
          conn.close()
          
      except Exception as e:
          print('Error:', e)
          try:
              conn.close()
          except:
              pass

if __name__ == '__main__':
  try:
      main()
  except KeyboardInterrupt:
      print('Server stopped')