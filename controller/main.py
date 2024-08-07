import network
import espnow

from machine import Pin, ADC
from time import sleep


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)

# peer = b'\x74\x4b\xbd\xa2\x08\x74'   # MAC address of peer's wifi interface
peer = b'\xff\xff\xff\xff\xff\xff'
try:
  e.add_peer(peer)      # Must add_peer() before send()
except OSError as exp:
  print(f'Skip to connect to network: {exp}')


px = ADC(Pin(34))
px.atten(ADC.ATTN_11DB)  #Full range: 3.3v
py = ADC(Pin(35))
py.atten(ADC.ATTN_11DB)

while True:
  x = px.read()
  y = py.read()
  print("x:", x, "y:", y)
  sleep(0.1)
  e.send(peer, str(x), True)
