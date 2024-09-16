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

LIVES = 8
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


def showEndAnimation():
    for j in range(0, 3):
        for i in range(0, 8):
            pixels.clear_all()
            pixels.set_rgb(i, 255, 0, 0, 100)
            pixels.show()
            sleep_ms(50)

        for i in range(7, -1, -1):
            pixels.clear_all()
            pixels.set_rgb(i, 255, 0, 0, 100)
            pixels.show()
            sleep_ms(50)


STATE_INIT = 0
STATE_PLAY = 1
STATE_LOOSE_LIFE = 2
STATE_END = 3
STATE_ERROR = -1

state = STATE_INIT

while True:
    if state == STATE_INIT:
        if checkModulinoPixels():
            state = STATE_PLAY
        else:
            state = STATE_ERROR

    elif state == STATE_PLAY:
        print("PLAY")
        color = a.get_color_label()
        print(color)

        if color == "BLACK":
            LIVES -= 1
            lostLifeAnimation()
            if LIVES > 0:
                state = STATE_LOOSE_LIFE
            elif LIVES == 0:
                state = STATE_END

        elif color == "RED":
            # random spin
            a.rotate(
                random.choice([30.0, 45.0, 90.0, 130.0, 150.0, 180.0, 275.0, 360.0]),
                "deg",
            )

        receiveAndExecuteFromEspNow()

    elif state == STATE_LOOSE_LIFE:
        print("LOOSE LIFE")

        receiveAndExecuteFromEspNow()

        if a.get_color_label() is not "BLACK":
            state = STATE_PLAY
        else:
            state = STATE_LOOSE_LIFE

    elif state == STATE_END:
        a.drive(0, 0)
        showEndAnimation()

    elif state == STATE_ERROR:
        a.drive(0, 0)
        while True:
            # Blink the LEDs forever
            a.left_led.set_color(1, 0, 0)
            a.right_led.set_color(1, 0, 0)
            sleep_ms(200)
            a.left_led.set_color(0, 0, 0)
            a.right_led.set_color(0, 0, 0)
            sleep_ms(200)

    sleep_ms(100)
