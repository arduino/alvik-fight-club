import network
import espnow
import struct
import sys

from modulino import ModulinoKnob, ModulinoButtons

# Robot3: "74:4d:bd:a0:49:e8"
# Robot4: "74:4d:bd:a2:08:74"

ALVIK_MAC = "ff:ff:ff:ff:ff:ff"

sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
e = espnow.ESPNow()
e.active(True)


def mac_str_to_bytes(mac_str):
    mac_str = mac_str.replace(":", "")
    return bytes.fromhex(mac_str)


_mac_peer = mac_str_to_bytes(ALVIK_MAC)

try:
    e.add_peer(_mac_peer)
except OSError as exp:
    print(f"Skip to connect to network: {exp}")

buttons = ModulinoButtons()
if not buttons.connected:
    print("🤷 No button modulino found")
    sys.exit()

knob = ModulinoKnob()
if not knob.connected:
    print("🤷 No knob modulino found")
    sys.exit()
knob.range = (-15, 15)  # (Optional) Set a value range

STOP = 0
GO_FORWARD = 1
GO_BACKWARD = 2
TURN_LEFT = 3
TURN_RIGHT = 4


def stop():
    e.send(_mac_peer, struct.pack("BHH", STOP), True)


def go_forward():
    e.send(_mac_peer, struct.pack("BHH", GO_FORWARD), True)


def go_backward():
    e.send(_mac_peer, struct.pack("BHH", GO_BACKWARD), True)


def turn_left():
    e.send(_mac_peer, struct.pack("BHH", TURN_LEFT), True)


def turn_right():
    e.send(_mac_peer, struct.pack("BHH", TURN_RIGHT), True)


buttons.on_button_a_press = lambda: go_forward()
buttons.on_button_b_press = lambda: stop()
buttons.on_button_c_press = lambda: go_backward()

knob.on_press = lambda: stop()
knob.on_rotate_clockwise = lambda steps, value: turn_left()
knob.on_rotate_counter_clockwise = lambda steps, value: turn_right()

while True:
    knob.update()
    buttons.update()
