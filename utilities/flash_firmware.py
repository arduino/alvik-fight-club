# from machine import reset
from arduino_alvik import update_firmware

# this is a patch to fix possible running threads on Alvik
from arduino_alvik import ArduinoAlvik

alvik = ArduinoAlvik()
alvik.stop()

update_firmware("./firmware_dev_1_0_3.bin")
# reset()
