# ZE15-CO Q&A Mode Test Program 20250204a
# https://github.com/ageagainstthemachine/ZE15-CO-CircuitPython-Test

# Import necessary libraries/modules
import board  # Import board module
import busio  # Import busio module to use UART (serial communication)
import time   # Import time module for delays

# === INITIALIZE UART COMMUNICATION ===
# The ZE15-CO sensor communicates using UART (serial communication).
# We set up UART on GP0 (TX - Transmit) and GP1 (RX - Receive).
# Baud rate must be 9600 to match the sensor's default setting.
# Timeout is set to 1 second to prevent blocking if no data is received.
uart = busio.UART(board.GP0, board.GP1, baudrate=9600, timeout=1)

# === Q&A MODE COMMAND TO REQUEST CO DATA ===
# This is a 9-byte command that tells the sensor to return a one-time reading.
INQUIRY_COMMAND = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])

def calculate_checksum(data):
    """
    Calculate the checksum for the received data.
    
    The checksum is computed by:
    1. Summing bytes 1 through 7 (excluding the start byte and checksum byte)
    2. Taking the bitwise negation (~) of the sum
    3. Adding 1 (two's complement)
    4. Keeping only the last 8 bits (AND 0xFF)

    This ensures that data integrity is verified.
    """
    checksum = sum(data[1:8])  # Sum bytes 1 through 7
    checksum = (~checksum + 1) & 0xFF  # Compute two's complement and keep last 8 bits
    return checksum

def parse_sensor_data(data):
    """
    Parses a 9-byte response from the ZE15-CO sensor in Q&A mode.
    
    Expected Response Format (9 bytes):

    Byte0   Byte1   Byte2   Byte3   Byte4   Byte5   Byte6   Byte7   Byte8
    0xFF    0x86    [HIGH]  [LOW]   0x00    0x00    [HIGH]  [LOW]   [CHK]

    Description of Each Byte:
    - Byte 0: Start byte (0xFF)
    - Byte 1: Command byte (0x86) specifying response mode
    - Byte 2: Concentration High Byte
    - Byte 3: Concentration Low Byte
    - Byte 4: Reserved (0x00)
    - Byte 5: Reserved (0x00)
    - Byte 6: Full range High Byte (Fixed at 0x13)
    - Byte 7: Full range Low Byte (Fixed at 0x88)
    - Byte 8: CChecksum (used for error detection)

    The CO concentration is stored in:
      (Byte 2 * 256 + Byte 3) * 0.1

    Returns:
        CO concentration in ppm if valid, otherwise None.
    """

    # === STEP 1: CHECK DATA LENGTH ===
    if len(data) != 9:
        print("Invalid data length (expected 9 bytes)")
        return None

    # === STEP 2: CHECK START BYTE & COMMAND BYTE ===
    if data[0] != 0xFF or data[1] != 0x86:
        print("Invalid response format (expected 0xFF 0x86 at start)")
        return None

    # === STEP 3: CHECKSUM VALIDATION ===
    received_checksum = data[8]  # Extract checksum from last byte
    calculated_checksum = calculate_checksum(data)

    if received_checksum != calculated_checksum:
        print(f"Checksum error! Received: {hex(received_checksum)}, Expected: {hex(calculated_checksum)}")
        return None
    else:
        print("Checksum valid")

    # === STEP 4: EXTRACT CO CONCENTRATION DATA ===
    high_byte = data[2]  # Byte 2: CO Concentration High Byte
    low_byte = data[3]   # Byte 3: CO Concentration Low Byte

    # === DEBUG: PRINT RAW BYTE VALUES ===
    print(f"High Byte: {hex(high_byte)} ({high_byte})")
    print(f"Low Byte: {hex(low_byte)} ({low_byte})")

    # === STEP 4: COMPUTE CO CONCENTRATION ===
    # Formula: (High Byte * 256 + Low Byte) * 0.1
    co_ppm = (high_byte * 256 + low_byte) * 0.1

    # === DEBUG: SHOW FINAL CALCULATION ===
    print(f"CO ppm Calculation: ({high_byte} * 256 + {low_byte}) * 0.1 = {co_ppm} ppm")

    return co_ppm  # Return calculated CO concentration

# === MAIN LOOP ===
while True:
    # === STEP 1: SEND INQUIRY COMMAND ===
    # The program will not read initiative upload mode data on its own in Q&A mode.
    # We must send the command to request a reading.
    uart.write(INQUIRY_COMMAND)
    print("\nSent CO Inquiry Command")

    # === STEP 2: WAIT FOR RESPONSE ===
    # The sensor needs time to process the request and send a response.
    time.sleep(1)  # Allow sensor time to process and respond

    # === STEP 3: READ SENSOR RESPONSE (9 bytes expected) ===
    if uart.in_waiting >= 9: # The sensor has sent the 9-byte response.
        raw_data = uart.read(9)  # Read full 9-byte packet

        # === STEP 4: PRINT RAW DATA FOR DEBUGGING ===
        if raw_data:
            print("\nReceived Data:", [hex(b) for b in raw_data])

            # === STEP 5: PARSE SENSOR RESPONSE DATA ===
            co_value = parse_sensor_data(raw_data)

            # === STEP 6: DISPLAY FINAL RESULT ===
            if co_value is not None:
                print(f"CO Concentration: {co_value:.1f} ppm")

    # === STEP 7: WAIT BEFORE NEXT REQUEST ===
    # We wait a few seconds before requesting another reading.
    time.sleep(5)  # Wait 5 seconds before sending the next inquiry
