# web_server.py
import socket
import json
import ure

class WebServer:
  def __init__(self, config):
      self.config = config
      self.server_socket = None
      self.routes = {
          '': self.handle_root,
          'command': self.handle_command,
          'pid': self.handle_pid_update,
          'mode': self.handle_mode_change
      }

  def start(self):
      """Start the web server"""
      addr = socket.getaddrinfo('0.0.0.0', self.config['port'])[0][-1]
      
      if self.server_socket:
          self.server_socket.close()
      
      self.server_socket = socket.socket()
      self.server_socket.bind(addr)
      self.server_socket.listen(1)
      
      print(f'Web server started on port {self.config["port"]}')
      return self.server_socket

  def handle_request(self, client_socket):
      """Handle incoming client requests"""
      try:
          client_socket.settimeout(self.config['timeout'])

          request = b""
          try:
              while b"\r\n\r\n" not in request:
                  request += client_socket.recv(512)
          except OSError:
              print("Timeout waiting for complete headers")
              return

          try:
              request += client_socket.recv(1024)
              print("Received additional form data")
          except OSError:
              pass

          request_str = request.decode('utf-8')
          print(f"Received request: {request_str[:100]}...")

          if "HTTP" not in request_str:
              print("Invalid request - no HTTP")
              return

          # Parse URL
          url = self.parse_url(request_str)
          if url is None:
              self.handle_not_found(client_socket, "Invalid URL")
              return

          # Route to appropriate handler
          handler = self.routes.get(url.split('/')[0], self.handle_not_found)
          handler(client_socket, request_str)

      except Exception as e:
          print(f"Error handling request: {str(e)}")
          self.send_error_response(client_socket, 500, f"Internal error: {str(e)}")
      finally:
          try:
              client_socket.close()
          except:
              pass

  def parse_url(self, request_str):
      """Parse URL from request string"""
      try:
          url_match = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request_str)
          if url_match:
              try:
                  return url_match.group(1).decode("utf-8").rstrip("/")
              except AttributeError:
                  return url_match.group(1).rstrip("/")
      except Exception as e:
          print(f"Error parsing URL: {e}")
      return None

  def handle_root(self, client, request):
      """Serve the main HTML page"""
      try:
          with open('index.html', 'r') as f:
              content = f.read()
          response = "HTTP/1.1 200 OK\r\n"
          response += "Content-Type: text/html\r\n\r\n"
          response += content
          client.send(response.encode())
      except Exception as e:
          print(f"Error serving root page: {e}")
          self.send_error_response(client, 500, "Error serving page")

  def handle_command(self, client, request):
      """Handle robot commands"""
      try:
          cmd_match = ure.search("cmd=([^&]*)", request)
          if cmd_match:
              cmd = cmd_match.group(1)
              print(f"Received command: {cmd}")
              
              response = "HTTP/1.1 200 OK\r\n"
              response += "Content-Type: text/plain\r\n\r\n"
              response += f"Command {cmd} processed"
          else:
              response = "HTTP/1.1 400 Bad Request\r\n\r\n"
              response += "Invalid command format"
          
          client.send(response.encode())
      except Exception as e:
          print(f"Error handling command: {e}")
          self.send_error_response(client, 500, "Error processing command")

  def handle_pid_update(self, client, request):
      """Handle PID updates"""
      try:
          body_start = request.find('\r\n\r\n') + 4
          body = request[body_start:]
          
          try:
              pid_values = json.loads(body)
              print(f"Updating PID values: {pid_values}")
              
              response = "HTTP/1.1 200 OK\r\n"
              response += "Content-Type: text/plain\r\n\r\n"
              response += "PID values updated"
          except json.JSONDecodeError:
              response = "HTTP/1.1 400 Bad Request\r\n\r\n"
              response += "Invalid JSON data"
              
          client.send(response.encode())
      except Exception as e:
          print(f"Error updating PID: {e}")
          self.send_error_response(client, 500, "Error updating PID values")

  def handle_mode_change(self, client, request):
      """Handle mode changes"""
      try:
          mode_match = ure.search("set=([^&]*)", request)
          if mode_match:
              mode = mode_match.group(1)
              print(f"Mode change requested: {mode}")
              response = "HTTP/1.1 200 OK\r\n"
              response += "Content-Type: text/plain\r\n\r\n"
              response += f"Mode changed to {mode}"
          else:
              response = "HTTP/1.1 400 Bad Request\r\n\r\n"
              response += "Invalid mode format"
              
          client.send(response.encode())
      except Exception as e:
          print(f"Error changing mode: {e}")
          self.send_error_response(client, 500, "Error changing mode")

  def handle_not_found(self, client, url):
      """Handle 404 Not Found"""
      response = "HTTP/1.1 404 Not Found\r\n"
      response += "Content-Type: text/plain\r\n\r\n"
      response += f"Path '{url}' not found"
      try:
          client.send(response.encode())
      except:
          pass

  def send_error_response(self, client, code, message):
      """Send error response"""
      response = f"HTTP/1.1 {code} Error\r\n"
      response += "Content-Type: text/plain\r\n\r\n"
      response += message
      try:
          client.send(response.encode())
      except:
          pass

  def stop(self):
      """Stop the web server"""
      if self.server_socket:
          self.server_socket.close()
          self.server_socket = None