import socket
import json

class WebServer:
  def __init__(self):
      self.handlers = {
          'command': None,
          'pid': None,
          'mode': None
      }

  def register_handler(self, handler_type, handler_function):
      """Register handlers for different types of requests"""
      if handler_type in self.handlers:
          self.handlers[handler_type] = handler_function

  def read_html(self):
      """Read the HTML file"""
      try:
          with open('index.html', 'r') as file:
              return file.read()
      except:
          return "Error: HTML file not found"

  def parse_request(self, request):
      """Parse incoming HTTP request"""
      try:
          # Serve main page
          if request.startswith('GET / '):
              return self._serve_main_page()
          
          # Handle movement commands
          elif 'GET /command?cmd=' in request:
              return self._handle_command(request)
          
          # Handle PID updates
          elif request.startswith('POST /pid'):
              return self._handle_pid_update(request)
          
          # Handle mode changes
          elif 'GET /mode?set=' in request:
              return self._handle_mode_change(request)
          
          else:
              return self._create_response('404 Not Found', 'text/plain', 'Not Found')
              
      except Exception as e:
          return self._create_response('500 Internal Server Error', 'text/plain', f'Error: {str(e)}')

  def _serve_main_page(self):
      """Serve the main HTML page"""
      return self._create_response('200 OK', 'text/html', self.read_html())

  def _handle_command(self, request):
      """Handle movement commands"""
      cmd = request.split('cmd=')[1].split(' ')[0]
      if self.handlers['command']:
          self.handlers['command'](cmd)
      return self._create_response('200 OK', 'text/plain', f'Command received: {cmd}')

  def _handle_pid_update(self, request):
      """Handle PID value updates"""
      try:
          body_start = request.find('\r\n\r\n') + 4
          body = request[body_start:]
          pid_values = json.loads(body)
          if self.handlers['pid']:
              self.handlers['pid'](pid_values)
          return self._create_response('200 OK', 'text/plain', 'PID values updated')
      except:
          return self._create_response('400 Bad Request', 'text/plain', 'Invalid PID data')

  def _handle_mode_change(self, request):
      """Handle mode changes"""
      mode = request.split('set=')[1].split(' ')[0]
      if self.handlers['mode']:
          self.handlers['mode'](mode)
      return self._create_response('200 OK', 'text/plain', f'Mode changed to: {mode}')

  def _create_response(self, status, content_type, content):
      """Create HTTP response"""
      return f'HTTP/1.1 {status}\nContent-Type: {content_type}\n\n{content}'