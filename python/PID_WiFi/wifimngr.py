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
  """Handle client connections with improved browser compatibility"""
  try:
      # Set timeout for client connection
      client_socket.settimeout(self.server_config['timeout'])

      # Accumulate the complete request
      request = b""
      try:
          # Keep reading until we get the end of headers
          while b"\r\n\r\n" not in request:
              request += client_socket.recv(512)
      except OSError:
          print("Timeout waiting for complete headers")
          return

      # Handle additional data (especially for Safari)
      try:
          # Try to receive any additional form data
          request += client_socket.recv(1024)
          print("Received additional form data")
      except OSError:
          pass  # No additional data available

      # Convert request to string for processing
      request_str = request.decode('utf-8')
      print(f"Received request: {request_str[:100]}...")  # Print first 100 chars

      # Skip invalid requests
      if "HTTP" not in request_str:
          print("Invalid request - no HTTP")
          return

      # Extract URL with version compatibility handling
      try:
          # Try modern parsing first
          url_match = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request_str)
          if url_match:
              try:
                  # For MicroPython versions that need decode
                  url = url_match.group(1).decode("utf-8").rstrip("/")
              except AttributeError:
                  # For versions where group is already a string
                  url = url_match.group(1).rstrip("/")
          else:
              raise ValueError("No URL match found")
      except Exception as e:
          print(f"Error parsing URL: {e}")
          self.handle_not_found(client_socket, "Invalid URL")
          return

      print(f"Processing URL: {url}")

      # Route the request
      if url == "":
          # Serve main page
          if self.handlers.get('root'):
              self.handlers['root'](client_socket)
          else:
              self.handle_root(client_socket)
      
      elif url == "config.js":
          # Serve configuration file
          self.serve_config_js(client_socket)
      
      elif url.startswith("command"):
          # Handle robot commands
          if self.handlers.get('command'):
              self.handlers['command'](client_socket, request_str)
          else:
              self.handle_not_found(client_socket, url)
      
      elif url.startswith("pid"):
          # Handle PID updates
          if self.handlers.get('pid'):
              self.handlers['pid'](client_socket, request_str)
          else:
              self.handle_not_found(client_socket, url)
      
      elif url.startswith("mode"):
          # Handle mode changes
          if self.handlers.get('mode'):
              self.handlers['mode'](client_socket, request_str)
          else:
              self.handle_not_found(client_socket, url)
      
      else:
          self.handle_not_found(client_socket, url)

  except Exception as e:
      print(f"Error handling client: {str(e)}")
      try:
          self.send_error_response(client_socket, 500, f"Internal error: {str(e)}")
      except:
          pass
  finally:
      try:
          client_socket.close()
      except:
          pass

def handle_not_found(self, client_socket, url):
  """Handle 404 Not Found responses"""
  response = f"HTTP/1.1 404 Not Found\r\n"
  response += "Content-Type: text/html\r\n\r\n"
  response += f"<h1>404 Not Found</h1><p>Path not found: {url}</p>"
  client_socket.send(response.encode())

def send_error_response(self, client_socket, code, message):
  """Send error response to client"""
  response = f"HTTP/1.1 {code} Error\r\n"
  response += "Content-Type: text/html\r\n\r\n"
  response += f"<h1>Error {code}</h1><p>{message}</p>"
  client_socket.send(response.encode())

def serve_config_js(self, client_socket):
  """Serve the configuration JavaScript file"""
  try:
      with open('config.js', 'r') as f:
          content = f.read()
      response = "HTTP/1.1 200 OK\r\n"
      response += "Content-Type: application/javascript\r\n\r\n"
      response += content
      client_socket.send(response.encode())
  except:
      self.send_error_response(client_socket, 404, "Configuration file not found")

  def stop(self):
      """Stop the WiFi manager"""
      if self.server_socket:
          self.server_socket.close()
          self.server_socket = None
      self.wlan_ap.active(False)    