import network
import espnow
import struct

from arduino_alvik import ArduinoAlvik

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

# print(sta.config('mac').hex())

e = espnow.ESPNow()
e.active(True)

# convert x from the input range [in_min, in_max] to the output range [out_min, out_max].
def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

a = ArduinoAlvik()
a.begin()

while True:
    host, msg = e.recv()
    if msg:
        if len(msg) < 6: # discard garbage
            continue
        unpacked_message = struct.unpack('BHH', msg)

        msg_type = unpacked_message[0]
        x = unpacked_message[1]
        y = unpacked_message[2]

        if int(msg_type) == 1:
          x, y = int(x), int(y)
          if 1750<=x<=1900: #hack: in normal position the joystick read 1700-1800 instead of 4095/2 = 2047
            x = 2047
          if 1750<=y<=1900: #hack: in normal position the joystick read 1700-1800 instead of 4095/2 = 2047
            y = 2047
          xm = map_value(x, 0, 4095, -100, 100) # rotation
          ym = map_value(y, 0, 4095, -50, 50) # bw, fw : from 10mm/s to 0
          print("moving", "x:", x, "y:", y, "mx", xm, "my", ym)
          a.drive(ym, -xm)
    else:
      print("timeout on receive")
