import network
import espnow
import struct
import random

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

try:
    from modulino import ModulinoPixels, ModulinoColor
except ImportError as e:
    print("ImportError: ModulinoPixels not installed")
    sys.exit(-1)

LIVES = 8
VELOCITY = 50  # mm/s TODO: set the correct value

STOP = 0
GO_FORWARD = 1
GO_BACKWARD = 2
TURN_LEFT = 3
TURN_RIGHT = 4

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
e = espnow.ESPNow()
e.active(True)

a = ArduinoAlvik()
a.begin()

pixels = ModulinoPixels()


def receiveAndExecuteFromEspNow():
    host, msg = e.recv(
            timeout_ms=0
        )  # TODO: See ESPNow.irecv() for a memory-friendly alternative.
    if msg is None:
        return
    if len(msg) < 6:  # discard garbage
        return
    unpacked_message = struct.unpack("BHH", msg)
    msg_type = unpacked_message[0]
    if int(msg_type) == STOP:
        a.drive(0, 0)
    elif int(msg_type) == GO_FORWARD:
        a.drive(VELOCITY, 0)
    elif int(msg_type) == GO_BACKWARD:
        a.drive(-VELOCITY, 0)
    elif int(msg_type) == TURN_LEFT:
        a.drive(0, 40)
    elif int(msg_type) == TURN_RIGHT:
        a.drive(0, -40)

def lostLifeAnimation():
    a.drive(0, 0)

    for i in range(3):
        a.left_led.set_color(1, 0, 0)
        a.right_led.set_color(1, 0, 0)
        sleep_ms(200)
        a.left_led.set_color(0, 0, 0)
        a.right_led.set_color(0, 0, 0)
        sleep_ms(200)

    pixels.clear_all()
    color = ModulinoColor.RED
    if LIVES >= 6:
        color = ModulinoColor.GREEN
    elif LIVES >= 3 and LIVES < 6:
        color = ModulinoColor(255, 156, 0)
    else:
        color = ModulinoColor.RED
    pixels.set_range_color(0, LIVES - 1, color, 70)
    pixels.show()

def checkModulinoPixels():
    ok_pixel = False
    retries = 3
    for x in range(retries):
        if pixels.connected:
            ok_pixel = True
            break
        else:
            a.left_led.set_color(1, 0, 0)
            a.right_led.set_color(1, 0, 0)
            sleep_ms(500)
    return ok_pixel

STATE_INIT = 0
STATE_PLAY = 1
STATE_LOOSE_LIFE = 2
STATE_END = 3
STATE_ERROR = -1

state = STATE_INIT

while True:
    if state == STATE_INIT:
        if(checkModulinoPixels()):
            state = STATE_PLAY
        else:
            state = STATE_ERROR

    elif state == STATE_PLAY:
        print("PLAY")
        color = a.get_color_label()
        print(color)

        if color == "BLACK":
            LIVES -= 1
            if LIVES > 0:
                lostLifeAnimation()
                state = STATE_LOOSE_LIFE
            elif LIVES == 0:
                state = STATE_END

        elif color == "RED":
            # random spin
            a.rotate(
                random.choice([30.0, 45.0, 90.0, 130.0, 150.0, 180.0, 275.0, 360.0]), "deg"
            )

        receiveAndExecuteFromEspNow()

    elif state == STATE_LOOSE_LIFE:
        print("LOOSE LIFE")

        receiveAndExecuteFromEspNow()

        if a.get_color_label() is not "BLACK":
            state = STATE_PLAY
        else:
             state = STATE_LOOSE_LIFE

    elif state == STATE_ERROR:
         while True:
            # Blink the LEDs forever
            a.left_led.set_color(1, 0, 0)
            a.right_led.set_color(1, 0, 0)
            sleep_ms(200)
            a.left_led.set_color(0, 0, 0)
            a.right_led.set_color(0, 0, 0)
            sleep_ms(200)

    sleep_ms(100)
