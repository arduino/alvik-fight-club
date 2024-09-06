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
	mpremote mip install github:arduino/arduino-modulino-mpy

.PHONY: robot-get-mac
robot-get-mac:
	mpremote exec "import network; print(':'.join('{:02x}'.format(x) for x in network.WLAN().config('mac')))"

.PHONY: robot-upload
robot-upload:
	mpremote fs cp  ./sketches/robot/main.py :main.py
	mpremote reset
