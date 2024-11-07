# main.py
from wifimngr import WiFiManager
import gc
from config import NETWORK, write_js_config
import network
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
  gc.collect()
  print(f"\nFree memory: {gc.mem_free()} bytes")
  
  # Check network
  
  ap = network.WLAN(network.AP_IF)
  print("\nNetwork status:")
  print(f"Active: {ap.active()}")
  if ap.active():
      print(f"Network: {ap.config('essid')}")
      print(f"IP Address: {ap.ifconfig()[0]}")




def main():
  try:
      print("\nInitializing Robot Control System...")
      
      # Generate configuration JavaScript file
      print("Generating configuration files...")
      write_js_config()
      
      # Initialize WiFi manager with network configuration
      print("Starting WiFi manager...")
      wifi_manager = WiFiManager(NETWORK)
      
      # Start access point
      ap_ip = wifi_manager.init_ap()
      print(f"Access Point started at {ap_ip}")
      
      # Start web server
      server_socket = wifi_manager.start_server()
      print("Web server started")
      
      print("\nSystem Ready!")
      print("=" * 40)
      
      # Main server loop
      while True:
          gc.collect()  # Clean up memory
          try:
              client, addr = server_socket.accept()
              print(f'\nNew client connected from: {addr}')
              wifi_manager.web_server.handle_request(client)
          except Exception as e:
              print(f'Connection error: {e}')

  except KeyboardInterrupt:
      print("\nShutdown requested...")
  except Exception as e:
      print(f'\nFatal error: {e}')
  finally:
      print("\nCleaning up...")
      try:
          wifi_manager.stop()
          print("WiFi manager stopped")
      except:
          pass
      print("System shutdown complete")

if __name__ == '__main__':
  check_system_status()
  main()