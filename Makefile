
.PHONY: init
init:
	pip install --user mpremote
	pip install black

.PHONY: install
install:
	# 1. Connect the board
	# 2. Check that no other software are running occupying the port (like microypthon ide)
	mpremote mip install github:arduino/arduino-modulino-mpy

.PHONY: fmt
fmt:
	black .
