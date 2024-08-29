import network
import espnow
import struct

from arduino_alvik import ArduinoAlvik

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


def updateHealthLeds():
    if not pixels.connected:
        print("🤷 No pixel modulino found")
        return
    if LIVES < 0:
        return
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


while True:
    updateHealthLeds()  # TODO: update health only when lives changes.
    host, msg = e.recv(
        timeout_ms=0
    )  # TODO: See ESPNow.irecv() for a memory-friendly alternative.
    if msg:
        if len(msg) < 6:  # discard garbage
            continue
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
