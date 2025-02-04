# ZE15-CO Sensor Tests (CircuitPython)

## Overview

This repository contains CircuitPython scripts (programs) for testing the **ZE15-CO** carbon monoxide sensor using UART communication on a Raspberry Pi Pico.

Currently included:
- [**Initiative Upload Mode Test**](<Initiative-Upload-Mode/code.py>) - Reads CO concentration automatically sent by the sensor every second.
- **(Planned) Question and Answer Mode Test** - Sends requests to the sensor and reads responses.

**Datasheet:** [ZE15-CO Official Datasheet](http://winsen-sensor.com/d/files/ZE15-CO.pdf)

---

## Hardware Setup

- **Sensor TX - Pico GP1 (RX)**
- **Sensor RX - Pico GP0 (TX)**
- **Sensor GND - Pico GND**
- **Sensor VCC - Pico 5V**

---

## UART Communication Protocol

The ZE15-CO sensor communicates using a UART (serial) interface at:

- **Baud Rate:** 9600
- **Data Bits:** 8
- **Stop Bits:** 1
- **Parity:** None

It supports two communication modes:

**Initiative Upload Mode (Default)**
- The sensor automatically sends a 9-byte data packet every 1 second.
- No commands are needed from the microcontroller.
- Each packet contains the CO concentration value in ppm.

**Data Format (9 bytes per packet)**  
```
Byte0   Byte1   Byte2   Byte3   Byte4   Byte5   Byte6   Byte7   Byte8
0xFF    0x04    0x03    0x01    [HIGH]  [LOW]   0x13    0x88    [CHK]
```
| Byte | Description |
|-------|------------|
| `0xFF` | Start byte |
| `0x04` | Gas type (CO) |
| `0x03` | Unit (ppm) |
| `0x01` | Number of decimal places (fixed at 0.1 ppm) |
| **[HIGH]** | CO Concentration High Byte |
| **[LOW]** | CO Concentration Low Byte |
| `0x13` | Full range high byte (fixed) |
| `0x88` | Full range low byte (fixed) |
| **[CHK]** | Checksum |

**CO Concentration Formula:**  
CO ppm = (HIGH * 256 + LOW) * 0.1

Example:  
```
Received Data: ['0xFF', '0x04', '0x03', '0x01', '0x00', '0x05', '0x13', '0x88', '0x58']
```
- **HIGH = `0x00` (0 in decimal)**
- **LOW = `0x05` (5 in decimal)**  
- **CO ppm = (0 * 256 + 5) * 0.1 = 0.5 ppm**

**Question & Answer Mode (Planned)**
- The microcontroller sends a **command request** to the sensor.
- The sensor **responds** with a CO concentration reading.
- This mode is activated automatically if a request is received.

**Request Packet Format (9 bytes)**  
```
0xFF  0x01  0x86  0x00  0x00  0x00  0x00  0x00  [CHK]
```

**Response Packet Format (9 bytes)**  
```
0xFF  0x86  [HIGH]  [LOW]  0x00  0x00  [HIGH]  [LOW]  [CHK]
```
*(Details to be implemented in the upcoming Q&A Mode test.)*

---

## Usage

1. Install **CircuitPython** on the Raspberry Pi Pico. ([Guide](https://circuitpython.org/board/raspberry_pi_pico/))
2. Copy `code.py` to the Pico.
3. Open a serial terminal (Mu Editor, Thonny, or screen).
4. View CO ppm readings which update every second.

---

## Future Plans

- Add a **Q&A Mode Test** to allow direct command-based readings.