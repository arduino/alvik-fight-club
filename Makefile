.PHONY: fmt
fmt:
	black .

.PHONY: init
init:
	pip install --user mpremote
	pip install black

.PHONY: controller-install
controller-install:
	mpremote mip install github:arduino/arduino-modulino-mpy

.PHONY: controller-upload
controller-upload:
	@if [ -z "$(robot-mac)" ]; then echo "Error: mac address not provided"; exit 1; fi
	sed -i 's/^ALVIK_MAC = .*/ALVIK_MAC = "$(robot-mac)"/' sketches/controller/main.py
	mpremote fs cp ./sketches/controller/main.py :main.py
	mpremote reset

.PHONY: robot-install
robot-install:
	mpremote mip install github:arduino/arduino-modulino-mpy github:arduino/ucPack-mpy

.PHONY: robot-get-mac
robot-get-mac:
	mpremote exec "import network; print(':'.join('{:02x}'.format(x) for x in network.WLAN().config('mac')))"


.PHONY: robot-get-charge
robot-get-charge:
	mpremote exec "from arduino_alvik import ArduinoAlvik; a = ArduinoAlvik(); a.begin(); print(a.get_battery_charge())"


.PHONY: robot-upload
robot-upload:
	mpremote fs cp  ./sketches/robot/main.py :main.py
	mpremote reset

.PHONY: robot-patch-firmware
robot-patch-firmware:
	# copy patched firmware of https://github.com/arduino-libraries/Arduino_AlvikCarrier/ into robot
	mpremote fs cp ./utilities/firmware_dev_1_0_3.bin :firmware_dev_1_0_3.bin
	# instal on STM32 using flash_firmware.py script
	mpremote run ./utilities/flash_firmware.py
	mpremote fs rm firmware_dev_1_0_3.bin

.PHONY: robot-patch-mpy
robot-patch-mpy:
	rm -rf arduino-alvik-mpy
	git clone git@github.com:arduino/arduino-alvik-mpy.git
	# See issue: https://github.com/bcmi-labs/alvik-fight-club/issues/38
	# See https://github.com/arduino/arduino-alvik-mpy/commit/177c43620b08ee6f66fac4d11839564eebddbd88
	cd arduino-alvik-mpy && git checkout 177c43620b08ee6f66fac4d11839564eebddbd88

	mpremote fs mkdir lib/arduino_alvik || true
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/__init__.py :lib/arduino_alvik/__init__.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/arduino_alvik.py :lib/arduino_alvik/arduino_alvik.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/constants.py :lib/arduino_alvik/constants.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/conversions.py :lib/arduino_alvik/conversions.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/pinout_definitions.py :lib/arduino_alvik/pinout_definitions.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/robot_definitions.py :lib/arduino_alvik/robot_definitions.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/stm32_flash.py :lib/arduino_alvik/stm32_flash.py
	mpremote fs cp ./arduino-alvik-mpy/arduino_alvik/uart.py :lib/arduino_alvik/uart.py
	mpremote reset
