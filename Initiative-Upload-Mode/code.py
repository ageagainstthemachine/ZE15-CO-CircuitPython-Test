# ZE15-CO Simple Iniative Upload Test Program 20250130a
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
    checksum = (~checksum + 1) & 0xFF  # Take two's complement and keep last 8 bits
    return checksum

def parse_sensor_data(data):
    """
    Parses a 9-byte response from the ZE15-CO sensor.
    
    Expected Data Format (from the datasheet):
    - Byte 0: Start byte (0xFF)
    - Byte 1: Gas type (0x04 for CO)
    - Byte 2: Unit (ppm) - Always 0x03
    - Byte 3: Number of decimal places - Always 0x01
    - Byte 4: Concentration High Byte
    - Byte 5: Concentration Low Byte
    - Byte 6: Full range High Byte (Fixed at 0x13)
    - Byte 7: Full range Low Byte (Fixed at 0x88)
    - Byte 8: Checksum (used for error detection)

    The CO concentration is stored in:
      (Byte 4 * 256 + Byte 5) * 0.1

    Returns:
        CO concentration in ppm if valid, otherwise None.
    """

    # === STEP 1: CHECK DATA LENGTH ===
    if len(data) != 9:
        print("Invalid data length (expected 9 bytes)")
        return None

    # === STEP 2: CHECK START BYTE ===
    if data[0] != 0xFF:
        print("Invalid start byte (expected 0xFF)")
        return None

    # === STEP 3: CHECKSUM VALIDATION ===
    received_checksum = data[8]  # Extract checksum from last byte
    calculated_checksum = calculate_checksum(data)  # Compute expected checksum

    if received_checksum != calculated_checksum:
        print(f"Checksum error! Received: {hex(received_checksum)}, Expected: {hex(calculated_checksum)}")
        return None
    else:
        print("Checksum valid")

    # === STEP 4: EXTRACT CO CONCENTRATION DATA ===
    high_byte = data[4]  # Byte 4: CO Concentration High Byte
    low_byte = data[5]   # Byte 5: CO Concentration Low Byte

    # === DEBUG: PRINT RAW BYTE VALUES ===
    print(f"High Byte: {hex(high_byte)} ({high_byte})")
    print(f"Low Byte: {hex(low_byte)} ({low_byte})")

    # === STEP 5: COMPUTE CO CONCENTRATION ===
    # Formula: (High Byte * 256 + Low Byte) * 0.1
    co_ppm = (high_byte * 256 + low_byte) * 0.1

    # === DEBUG: SHOW FINAL CALCULATION ===
    print(f"CO ppm Calculation: ({high_byte} * 256 + {low_byte}) * 0.1 = {co_ppm} ppm")

    return co_ppm  # Return calculated CO concentration

# === MAIN LOOP ===
while True:
    # === STEP 1: CHECK IF SENSOR HAS SENT DATA ===
    if uart.in_waiting >= 9:  # The sensor sends 9-byte packets every second
        raw_data = uart.read(9)  # Read the full 9-byte packet

        # === STEP 2: PRINT RAW DATA FOR DEBUGGING ===
        if raw_data:
            print("\nReceived Data:", [hex(b) for b in raw_data])

            # === STEP 3: PARSE THE SENSOR DATA ===
            co_value = parse_sensor_data(raw_data)

            # === STEP 4: DISPLAY FINAL RESULT ===
            if co_value is not None:
                print(f"CO Concentration: {co_value:.1f} ppm")

    # === STEP 5: WAIT BEFORE NEXT READ ===
    time.sleep(1)  # Wait for 1 second before checking again
