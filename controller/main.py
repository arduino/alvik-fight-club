import network
import espnow
import struct

from machine import Pin, ADC
from time import sleep


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)

peer = b'\xff\xff\xff\xff\xff\xff' # TODO: use MAC of alvik, not the broadcast
try:
  e.add_peer(peer)      # Must add_peer() before send()
except OSError as exp:
  print(f'Skip to connect to network: {exp}')


px = ADC(Pin(34))
px.atten(ADC.ATTN_11DB)       #Full range: 3.3v
py = ADC(Pin(35))
py.atten(ADC.ATTN_11DB)

while True:
  x = px.read() & 0xFFFF  # Ensure x is within 2 bytes range (0-65535)
  y = py.read() & 0xFFFF  # Ensure y is within 2 bytes range (0-65535)

  # Protocol definition: 6 bytes (1 byte for msg type, 2 bytes first argument, 2 bytes second argument)
  msg_type = 1
  message = struct.pack('BHH',msg_type, x, y)
  unpacked_message = struct.unpack('BHH', message)
  e.send(peer, message, True)

  sleep(0.1)
