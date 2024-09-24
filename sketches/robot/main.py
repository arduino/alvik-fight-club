import network
import espnow
import struct
import random
import sys

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

try:
    from modulino import ModulinoPixels, ModulinoColor
except ImportError as e:
    print("ImportError: ModulinoPixels not installed")
    sys.exit(-1)

VELOCITY = 13  # cm/s (max is 13cm/s)
ANGULAR_VELOCITY = 320  # (max 320.8988764044944)


STOP = 0
GO_FORWARD = 1
GO_BACKWARD = 2
TURN_LEFT = 3
TURN_RIGHT = 4
LIFT = 5

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
e = espnow.ESPNow()
e.active(True)

a = ArduinoAlvik()
a.begin()

pixels = ModulinoPixels(a.i2c)


lifState = 0        # 0 = down, 1 = up

def receiveAndExecuteFromEspNow():
    global lifState
    _, msg = e.recv(
        timeout_ms=0
    )  # TODO: See ESPNow.irecv() for a memory-friendly alternative.
    if msg is None:
        return
    if len(msg) < 1:  # discard garbage
        return
    unpacked_message = struct.unpack("B", msg)
    msg_type = unpacked_message[0]
    if int(msg_type) == STOP:
        a.drive(0, 0)
    elif int(msg_type) == GO_FORWARD:
        a.drive(-VELOCITY, 0)
    elif int(msg_type) == GO_BACKWARD:
        a.drive(VELOCITY, 0)
    elif int(msg_type) == TURN_LEFT:
        a.drive(0, ANGULAR_VELOCITY)
    elif int(msg_type) == TURN_RIGHT:
        a.drive(0, -ANGULAR_VELOCITY)
    elif int(msg_type) == LIFT:
        if lifState == 0:
            liftUp()
            lifState = 1
        else:
            liftDown()
            lifState = 0
    else:
      print("unknown command type ", msg_type)

def liftUp():
    a.set_servo_positions(180, 0)
    sleep_ms(25)
    a.set_servo_positions(175, 5)
    sleep_ms(25)
    a.set_servo_positions(170, 10)
    sleep_ms(25)
    a.set_servo_positions(165, 15)
    sleep_ms(25)
    a.set_servo_positions(160, 20)
    sleep_ms(25)


def liftDown():
    a.set_servo_positions(165, 15)
    sleep_ms(25)
    a.set_servo_positions(170, 10)
    sleep_ms(25)
    a.set_servo_positions(175, 5)
    sleep_ms(25)
    a.set_servo_positions(180, 0)


def showReadyToPlayAnimation():
    for _ in range(2):
        pixels.set_all_color(ModulinoColor.GREEN, 15)
        pixels.show()
        sleep_ms(250)
        pixels.clear_all()
        pixels.show()
        sleep_ms(250)

    pixels.set_all_color(ModulinoColor.GREEN, 15)
    pixels.show()


def showEndAnimation():
    for i in range(0, 8):
        pixels.clear_all()
        pixels.set_rgb(i, 255, 0, 0, 15)
        pixels.show()
        sleep_ms(50)

    for i in range(7, -1, -1):
        pixels.clear_all()
        pixels.set_rgb(i, 255, 0, 0, 15)
        pixels.show()
        sleep_ms(50)


STATE_INIT = 0
STATE_PLAY = 1
STATE_END = 2

state = STATE_INIT

while True:
    if state == STATE_INIT:
        a.drive(0, 0)
        showEndAnimation()
        if a.get_color_label() is not "BLACK":
            showReadyToPlayAnimation()
            state = STATE_PLAY

    elif state == STATE_PLAY:
        receiveAndExecuteFromEspNow()
        color = a.get_color_label()
        if color == "BLACK":
            state = STATE_INIT
        elif color == "RED":
            # random spin
            a.rotate(
                random.choice([30.0, 45.0, 90.0, 130.0, 150.0, 180.0, 275.0, 360.0]),
                "deg",
        )

    sleep_ms(50)
