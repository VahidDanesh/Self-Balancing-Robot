import network
import socket
import ure
import time
from config import NETWORK

class WiFiManager:
  def __init__(self):
      self.ap_config = NETWORK['AP']
      self.sta_config = NETWORK['STA']
      self.server_config = NETWORK['SERVER']
      
      self.wlan_ap = network.WLAN(network.AP_IF)
      self.wlan_sta = network.WLAN(network.STA_IF)
      self.server_socket = None
      
  def init_ap(self):
      """Initialize Access Point"""
      self.wlan_ap.active(True)
      self.wlan_ap.config(
          essid=self.ap_config['ssid'],
          password=self.ap_config['password'],
          authmode=self.ap_config['authmode'],
          max_clients=self.ap_config['max_clients']
      )
      
      while not self.wlan_ap.active():
          pass
      
      print('\n=== WiFi Access Point Created ===')
      print(f'1. Connect to WiFi network: "{self.ap_config["ssid"]}"')
      print(f'2. Use password: "{self.ap_config["password"]}"')
      print(f'3. Open browser and go to: http://{self.wlan_ap.ifconfig()[0]}')
      print('================================\n')
      
      return self.wlan_ap.ifconfig()[0]  # Return AP IP address

  def read_profiles(self):
      """Read saved WiFi profiles"""
      try:
          with open(self.sta_config['profiles_file']) as f:
              lines = f.readlines()
          profiles = {}
          for line in lines:
              ssid, password = line.strip("\n").split(";")
              profiles[ssid] = password
          return profiles
      except OSError:
          return {}

  def write_profiles(self, profiles):
      """Save WiFi profiles"""
      lines = []
      for ssid, password in profiles.items():
          lines.append("%s;%s\n" % (ssid, password))
      with open(self.sta_config['profiles_file'], "w") as f:
          f.write(''.join(lines))

  def start_web_server(self):
      """Start the configuration web server"""
      addr = socket.getaddrinfo('0.0.0.0', self.server_config['port'])[0][-1]

      if self.server_socket:
          self.server_socket.close()
      
      self.server_socket = socket.socket()
      self.server_socket.bind(addr)
      self.server_socket.listen(1)
      
      print(f'Web server started on {addr}')
      return self.server_socket

  def handle_client(self, client_socket):
      """Handle client connections"""
      try:
          client_socket.settimeout(self.server_config['timeout'])
          request = client_socket.recv(1024).decode()
          
          # Parse request and handle accordingly
          if request.startswith('GET /'):
              response = self.handle_get_request(request)
          elif request.startswith('POST /'):
              response = self.handle_post_request(request)
          else:
              response = self.create_error_response(400, "Invalid request")
          
          client_socket.send(response.encode())
          
      except Exception as e:
          print(f"Error handling client: {e}")
      finally:
          client_socket.close()

  def stop(self):
      """Stop the WiFi manager"""
      if self.server_socket:
          self.server_socket.close()
          self.server_socket = None
      self.wlan_ap.active(False)