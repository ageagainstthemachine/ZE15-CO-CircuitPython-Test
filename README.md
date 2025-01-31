# ZE15-CO Sensor Tests (CircuitPython)

## Overview

This repository contains CircuitPython scripts (programs) for testing the **ZE15-CO** carbon monoxide sensor using UART communication on a Raspberry Pi Pico.

Currently included:
- [**Initiative Upload Mode Test**](<Initiative-Upload-Mode/code.py>) - Reads CO concentration automatically sent by the sensor every second.
- **(Planned) Question and Answer Mode Test** - Sends requests to the sensor and reads responses.

## Hardware Setup

- **Sensor TX - Pico GP1 (RX)**
- **Sensor RX - Pico GP0 (TX)**
- **Sensor GND - Pico GND**
- **Sensor VCC - Pico 5V**

## Usage

1. Install **CircuitPython** on the Raspberry Pi Pico. ([Guide](https://circuitpython.org/board/raspberry_pi_pico/))
2. Copy 'code.py' to the Pico.
3. Open a serial terminal (Mu Editor, Thonny, or screen).
4. View CO ppm readings.

## Future Plans

- Add a **Q&A Mode Test** to allow direct command-based readings.