# wifimngr.py
import network
from web_server import WebServer

class WiFiManager:
  def __init__(self, network_config):
      """Initialize WiFi manager with network configuration"""
      self.ap_config = network_config['AP']
      self.sta_config = network_config['STA']
      self.server_config = network_config['SERVER']
      
      # Initialize network interfaces
      self.wlan_ap = network.WLAN(network.AP_IF)
      self.wlan_sta = network.WLAN(network.STA_IF)
      
      # Initialize web server
      self.web_server = WebServer(self.server_config)

  def init_ap(self):
      """Initialize Access Point"""
      self.wlan_ap.active(True)
      self.wlan_ap.config(
          essid=self.ap_config['ssid'],
          password=self.ap_config['password'],
          authmode=self.ap_config['authmode'],
          max_clients=self.ap_config['max_clients']
      )
      
      # Wait for AP to be active
      while not self.wlan_ap.active():
          pass
      
      ap_ip = self.wlan_ap.ifconfig()[0]
      
      print('\n=== WiFi Access Point Created ===')
      print(f'1. Connect to WiFi network: "{self.ap_config["ssid"]}"')
      print(f'2. Use password: "{self.ap_config["password"]}"')
      print(f'3. Open browser and go to: http://{ap_ip}')
      print('================================\n')
      
      return ap_ip

  def start_server(self):
      """Start the web server"""
      return self.web_server.start()

  def stop(self):
      """Stop WiFi manager and web server"""
      try:
          self.web_server.stop()
          print("Web server stopped")
      except:
          pass
      
      try:
          self.wlan_ap.active(False)
          print("WiFi AP disabled")
      except:
          pass