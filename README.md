# alvik-fight-club

Requirements:
  - Arduino Lab for [micropython](https://labs.arduino.cc/en/labs/micropython)
  - 1 Alvik
  - 1 Esp32 WROOM 32D (ohter board can be used but currenlty I tested using this one)
  - 1 joystick (like `https://www.rseonlineshop.co.za/collections/arduino-accessories/products/joystick-for-arduino-5v`)

Wiring joystick
  - `GND` to `GND` of esp32
  - `+5v` to `3v3` of esp 32
  - `VRx` to pin `35` of Esp32
  - `VRy` to pin `34` of Esp32

### Arduino Nano ESP32 and Modulino based remote control
The new version of the Alvik Fight Club remote control consists of the a 3D printed base [STL-file](cad/remote-control/remote-control.stl) and the following components:
|   | Description | Amount / € |
|---|---|:-:|
| 1 | [Arduino Nano ESP32 w/ headers](https://store.arduino.cc/products/nano-esp32-with-headers) | 23,20 € (Arduino) |
| 1 | Modulino buttons | Arduino |
| 1 | Modulino rotary encoder | Arduino |
| 2 | QWICC cables | Arduino |
| 1 | [SparkFun Qwiic Shield for Arduino Nano](https://www.sparkfun.com/products/16789) | 2,48 € |
| 8 | [M3 x 8 mm cutting screw](https://www.schraubenking.at/3-x-8mm-Flachrundkopfschraube-TX-fuer-Thermoplaste-P007210) | 1,20 € |
| 1 | Small USB battery pack | ? |
| 1 | 3D printed body | |

### Install MicroPython on `ESP32 WROOM 32D`
- Install micropython on the board `ESP32 WROOM 32D` (the controller board) I followed this [guide](https://micropython.org/download/ESP32_GENERIC/).
  - Download the [esptool](https://github.com/espressif/esptool)
  - Erase the flash: `esptool --chip esp32 --port /dev/ttyUSB1 erase_flash `
  - Download the firmware (like `ESP32_GENERIC-20240602-v1.23.0`)
  - Install the fw on the board `esptool --chip esp32 --port /dev/ttyUSB1 --baud 460800 write_flash -z 0x1000 ./ESP32_GENERIC-20240602-v1.23.0.bin`

Alternative: use the [MicroPython Installer](https://labs.arduino.cc/en/labs/micropython-installern) but I didn't test with the board Esp32 32D.

### Local dev
- Open `Arduino Lab for Micropython `
- Connect the alvik, copy the `robot/main.py` into the `main.py` in the  board
- Connect the `Esp32 WROOM 32D`, copy the `controller/main.py` into the `main.py` in the board
