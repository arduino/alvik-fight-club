import network
import espnow
import struct
import random
import sys
import machine

from arduino_alvik import ArduinoAlvik
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

try:
    from modulino import ModulinoPixels, ModulinoColor
except ImportError as e:
    print("ImportError: ModulinoPixels not installed")
    sys.exit(-1)

LINEAR_VELOCITY = 10    # (max 13cm/s)
ANGULAR_VELOCITY = 75  # (max 320.8988764044944)
FREEZE_FOR_SECONDS = 5
REVERT_CONTROLLER_FOR_SECONDS = 10


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
e = espnow.ESPNow()
e.active(True)

a = ArduinoAlvik()
a.begin()

pixels = ModulinoPixels(a.i2c)


STOP = 0
GO_FORWARD = 1
GO_BACKWARD = 2
TURN_LEFT = 3
TURN_RIGHT = 4
LIFT = 5


isPlayingReverted = False  # if true the controller action are reverted
lifState = 0  # 0 = down, 1 = up

lin = 0
ang = 0
def receiveAndExecuteFromEspNow():
    global lifState
    global lin
    global ang
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
        lin, ang = 0, 0
    elif int(msg_type) == GO_FORWARD:
        lin = LINEAR_VELOCITY if isPlayingReverted else -LINEAR_VELOCITY
        ang = 0
    elif int(msg_type) == GO_BACKWARD:
        lin = -LINEAR_VELOCITY if isPlayingReverted else LINEAR_VELOCITY
        ang = 0
    elif int(msg_type) == TURN_LEFT:
        ang = -ANGULAR_VELOCITY if isPlayingReverted else ANGULAR_VELOCITY
    elif int(msg_type) == TURN_RIGHT:
        ang = ANGULAR_VELOCITY if isPlayingReverted else -ANGULAR_VELOCITY
    elif int(msg_type) == LIFT:
        if lifState == 0:
            liftUp()
            lifState = 1
        else:
            liftDown()
            lifState = 0
    else:
        print("unknown command type ", msg_type)

    a.drive(lin, ang)

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


def showReadyToPlayLeds():
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


def map_value(value, from_low, from_high, to_low, to_high):
    return int(
        (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low
    )


def countdown_color(color, ledoff_every_tick=2):
    for i in range(7, 0, -ledoff_every_tick):
        pixels.set_range_color(0, i, color)
        pixels.show()
        sleep_ms(500)
        pixels.clear_all()
        pixels.show()
        sleep_ms(500)
    pixels.clear_all()
    pixels.show()

def calibrate_color():
    print("Reading white color")
    countdown_color(ModulinoColor.WHITE)
    a.color_calibration("white")

    pixels.set_all_color(ModulinoColor.GREEN, 15)
    pixels.show()
    sleep_ms(2000)

    print("Reading black color")
    countdown_color(ModulinoColor.BLUE)
    a.color_calibration("black")

    pixels.set_all_color(ModulinoColor.GREEN, 15)
    pixels.show()
    sleep_ms(2000)

    pixels.clear_all()
    pixels.show()

    # hard-reset the board to refresh the calibration (read again the color from the file)
    machine.reset()


STATE_SETUP = -1
STATE_INIT = 0
STATE_PLAY = 1

state = STATE_INIT

deadline = 0
while True:
    try:
        if state == STATE_SETUP:
            calibrate_color()

        if state == STATE_INIT:
            a.drive(0, 0)
            showEndAnimation()
            if a.get_touch_ok():
                state = STATE_SETUP
            if a.get_color_label() is not "BLACK":
                showReadyToPlayLeds()
                state = STATE_PLAY

        elif state == STATE_PLAY:
            receiveAndExecuteFromEspNow()

            if a.get_touch_ok():
                state = STATE_SETUP

            color = a.get_color_label()
            if color == "BLACK":
                state = STATE_INIT
            elif color == "YELLOW":
                pixels.set_all_color(ModulinoColor.YELLOW, 15)
                pixels.show()
                deg = random.choice([30.0, 45.0, 90.0, 130.0, 150.0, 180.0, 275.0, 360.0])
                a.rotate(deg, "deg")
                showReadyToPlayLeds()
            elif color == "BLUE":
                a.drive(0, 0)
                for x in range(0, FREEZE_FOR_SECONDS):
                    sleep_ms(500)
                    pixels.set_all_color(ModulinoColor.BLUE, 15)
                    pixels.show()
                    sleep_ms(500)
                    pixels.clear_all()
                    pixels.show()
                showReadyToPlayLeds()
            elif color == "GREEN" or color == "LIGHT GREEN":
                if not isPlayingReverted:
                    deadline = ticks_add(ticks_ms(), REVERT_CONTROLLER_FOR_SECONDS * 1000)
                    isPlayingReverted = True

            if isPlayingReverted:
                elapsed = ticks_diff(deadline, ticks_ms())
                mapped = map_value(elapsed, 0, REVERT_CONTROLLER_FOR_SECONDS * 1000, 0, 7)
                pixels.clear_all()
                pixels.set_range_color(0, mapped, ModulinoColor.VIOLET)
                pixels.show()
                if elapsed < 0:
                    showReadyToPlayLeds()
                    isPlayingReverted = False
    except AssertionError:
        print("AssertionError")
        # If calibration is not done correctly, the _limit() function can raise an AssertError
        # See https://github.com/arduino/arduino-alvik-mpy/blob/80e66561a2ae06c69adddb3adc21ca88f91a57dd/arduino_alvik/arduino_alvik.py#L724
        state = STATE_SETUP
        continue
    sleep_ms(50)
