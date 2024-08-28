import network
import espnow
import struct

from machine import Pin, ADC
from time import sleep
from modulino import ModulinoKnob, ModulinoButtons

STOP = 0
GO_FORWARD = 1
GO_BACKWARD = 2
TURN_LEFT = 3
TURN_RIGHT = 4

PEER = b"\xff\xff\xff\xff\xff\xff"  # TODO: use MAC of alvik, not the broadcast

sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
e = espnow.ESPNow()
e.active(True)

try:
    e.add_peer(PEER)
except OSError as exp:
    print(f"Skip to connect to network: {exp}")

buttons = ModulinoButtons()
if not buttons.connected:
    print("🤷 No button modulino found")
    exit()

knob = ModulinoKnob()
if not knob.connected:
    print("🤷 No knob modulino found")
    exit()
knob.range = (-15, 15)  # (Optional) Set a value range


def stop():
    e.send(PEER, struct.pack("BHH", STOP), True)


def go_forward():
    e.send(PEER, struct.pack("BHH", GO_FORWARD), True)


def go_backward():
    e.send(PEER, struct.pack("BHH", GO_BACKWARD), True)


def turn_left():
    e.send(PEER, struct.pack("BHH", TURN_LEFT), True)


def turn_right():
    e.send(PEER, struct.pack("BHH", TURN_RIGHT), True)


buttons.on_button_a_press = lambda: go_forward()
buttons.on_button_b_press = lambda: stop()
buttons.on_button_c_press = lambda: go_backward()

knob.on_press = lambda: stop()
knob.on_rotate_clockwise = lambda steps, value: turn_left()
knob.on_rotate_counter_clockwise = lambda steps, value: turn_right()

while True:
    knob.update()
    buttons.update()
