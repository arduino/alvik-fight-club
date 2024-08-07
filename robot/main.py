import network
import espnow

from arduino_alvik import ArduinoAlvik

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

print(sta.config('mac').hex())

e = espnow.ESPNow()
e.active(True)

# convert x from the input range [in_min, in_max] to the output range [out_min, out_max].
def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

a = ArduinoAlvik()
a.begin()

while True:
    print("start receiving...")
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv()
        v = int(msg)
        m = map_value(v, 0, 4095, -10, 10) # from 10mm/s to 0
        print("value:", v, "m:", m)
        a.drive(m, 0)
    else:
      print("timeout on receive")
