try:
  import usocket as socket
except:
  import socket

from machine import Pin
from machine import sleep
from machine import reset
import time
import network
import ubinascii
import esp
import server
import gc
import json
import sys
import webrepl
from dev import Dht11, Relay

esp.osdebug(None)
gc.collect()

# Load config from config.json
print('Loading config...')
with open('config.json') as config_file:
	config = json.load(config_file)

IS_CONFIGURED = config['IS_CONFIGURED']
if IS_CONFIGURED=='NO':
  # Start in AP mode and run config page
  print("Network not configured. Starting AP...")
  
  ap = network.WLAN(network.AP_IF)
  ap.active(True)
  ap.config(essid="IntelliSwitch setup", password="esp32")
  print(ap.ifconfig())
  apconfig = ap.ifconfig()
  # sys.exit()
  # Web server init
  print('Writing config.js...')
  print(apconfig[0])
  with open("www/init/scripts/config.js",'w') as f:
    f.write("const device_ip = \"%s\"" % (apconfig[0]))
  print("Starting web server...")
  server.start_server_init()

# Define pins, init sensors
print('Init pins and devs...')
try:
  led_pin = Pin(config['LED_PIN'], Pin.OUT)
  led_pin.value(0)
  relay = Relay(config['RELAY_PIN'])
  dht11 = Dht11(config['DHT_PIN'])
except:
  print("Error init sensors!")
#-----------------------------#


# Connect WiFi
print("Configuring WiFi...")
station = network.WLAN(network.STA_IF)
if config['AUTO_IP_CONFIG']=="NO":
  print('Autoconfig = NO')
  print('Reading IP config from file...')
  station.ifconfig((config['WIFI_IP'],config['WIFI_MASK'],config['WIFI_DNS'],config['WIFI_GATEWAY']))
station.active(True)
print('Connect to AP...'+config['WIFI_SSID'])
station.connect(config['WIFI_SSID'], config['WIFI_PASS'])

retry_counter=0
print('Waiting for connection to AP...')
while station.isconnected() == False:
  if retry_counter<30:
    retry_counter=retry_counter+1
    # inverse LED
    print("Connecting... %s" % str(retry_counter))
    time.sleep(1)
  else:
    config['IS_CONFIGURED']="NO"
    with open('config.json', 'w') as f:
      json.dump(config, f)
    print('saved')
    reset()
  


if config['AUTO_IP_CONFIG']=="YES":
  # Read current connecton info and write to config.json
  print('Autoconfig = YES')
  print('Reading current connection parameters and save to config.json')
  ifconfig = station.ifconfig()
  config['WIFI_IP'] = ifconfig[0]
  config['WIFI_MASK'] = ifconfig[1]
  config['WIFI_DNS'] = ifconfig[2]
  config['WIFI_GATEWAY'] = ifconfig[3]
  config['AUTO_IP_CONFIG'] = "NO"
  print('Saving to file...')
  with open('config.json', 'w') as f:
    json.dump(config, f)
  print('saved')

print('Connection successful')
print(station.ifconfig())
print('Writing config.js...')
with open("www/scripts/config.js",'w') as f:
  f.write("const device_ip = \"%s\"" % (config['WIFI_IP']))
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)
#-----------------------------#

# Web server init
try:
  print("Starting web server...")
  server.start_server(relay, dht11)
except:
  print("Failed to start server")
  print("Attempt to start WebRepl")
  webrepl.start()
print("Starting REPL...")
webrepl.start()
#-----------------------------#
