# Network Configuration
NETWORK = {
  'ssid': 'RobotControl',
  'password': 'robot123',
  'authmode': 3  # WPA2
}

# PID Configuration
PID = {
  'kp': {
      'default': 100.00,
      'min': 0,
      'max': 2.00,
      'step': 0.01
  },
  'ki': {
      'default': 0.50,
      'min': 0,
      'max': 1.00,
      'step': 0.01
  },
  'kd': {
      'default': 0.25,
      'min': 0,
      'max': 0.50,
      'step': 0.01
  }
}

# Robot Modes
MODES = {
  'default': 'balance',
  'available': ['balance', 'avoid', 'roam']
}

# Motor Configuration
MOTOR = {
  'default_speed': 0,
  'max_speed': 1023,
  'min_speed': -1023,
  'acceleration_step': 100,
  'turn_difference': 200
}

# Web Server Configuration
SERVER = {
  'port': 80,
  'max_connections': 5
}

# Generate JavaScript configuration
def generate_js_config():
  return f"""
// Auto-generated from config.py
const CONFIG = {{
  pid: {str(PID).replace("'", '"')},
  modes: {str(MODES).replace("'", '"')},
  motor: {str(MOTOR).replace("'", '"')}
}};
"""

# Function to write configuration to JavaScript file
def write_js_config():
  with open('config.js', 'w') as f:
      f.write(generate_js_config())
