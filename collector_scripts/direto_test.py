import asyncio
import struct
from bleak import BleakClient, BleakScanner

# Replace with the name of your BLE device
DEVICE_NAME = "DIRETO XR"
CHARACTERISTIC_RESISTANCE_UUID = "00002ad9-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_NOTIFY_UUID = "00002ad2-0000-1000-8000-00805f9b34fb"

async def find_device_by_name(device_name):
    """
    Scan for BLE devices and return the address of the device matching the given name.
    """
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == device_name:
            print(f"Found device: {device.name} with address: {device.address}")
            return device.address
    print("Device not found. Ensure it is powered on and in range.")
    return None

async def notify_resistance_callback(self, sender):
    pass

async def write_resistance(client, characteristic, value):
    """
    Write a resistance value to the BLE device.
    """
    try:
        await client.start_notify(characteristic, notify_resistance_callback) # characteristic.uuid  
    
    except Exception as e:
            print("Error: ", e) 
    
    try:
        print(f"Writing resistance value: {value}")

        # Write the value to the characteristic
        await client.write_gatt_char(characteristic, bytearray([0x04, int(value)]))
        await asyncio.sleep(0.25)
        
    except Exception as e:
            print("Error: ", e) 
            
    try:
        await client.stop_notify(characteristic)
        
    except Exception as e:
        print(f"Failed to write resistance: {e}")

async def read_console_and_write(client, characteristic):
    """
    Continuously read values from the console and write them to the BLE device.
    """
    print("Enter resistance values between 0-256. Type 'exit' to quit.")
    loop = asyncio.get_event_loop()
    while True:
        try:
            # Run the blocking input() in a separate thread to prevent blocking the event loop
            user_input = await loop.run_in_executor(None, input, "Resistance (0-100): ")
            if user_input.lower() == 'exit':
                print("Exiting...")
                # Optionally, you can perform cleanup or notify other tasks here
                break

            # Convert input to an integer and validate the range
            value = int(user_input)
            if 0 <= value <= 256:
                # Write the value to the BLE device
                await write_resistance(client, characteristic, value)
            else:
                print("Please enter a value between 0 and 256.")
        except ValueError:
            print("Invalid input. Please enter a numeric value between 0 and 100.")

async def main():
    """
    Main function to find the device, connect, and continuously write resistance values.
    """
    device_address = await find_device_by_name(DEVICE_NAME)
    if not device_address:
        print("Device not found. Exiting.")
        return

    print("Connecting to BLE device...")
    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print("Failed to connect to the BLE device.")
            return

        print("Connected to BLE device.")

        # Continuously read console input and write values
        await asyncio.gather(
            asyncio.create_task(read_console_and_write(client, CHARACTERISTIC_RESISTANCE_UUID)),
            asyncio.create_task(read_data_from_direto(client))
        )

async def read_data_from_direto(client):
   
    
    try:
        await client.start_notify(CHARACTERISTIC_NOTIFY_UUID, notify_speed_callback)
        
    except Exception as e:
            print("Error: ", e) 
    
    
async def notify_speed_callback(sender, data):
   # global speed_queue
    # Convert the byte data to the speed value
    #speed_value = int.from_bytes(data, byteorder='little')  # Adjust based on your data format


    if struct.pack("@h", 1) == struct.pack("<h", 1):
        data = data[::-1]  # Reverse the byte order if little-endian

    result = struct.unpack_from(">h", data, 2)[0]
    output = result * 0.01
    if output < 0:
        output = abs(output)

    normalized_output_speed = normalize_speed_value(output, 0.0, 2.5)
    #print(f"Received speed : {normalized_output_speed}")
    log_received_speed(normalized_output_speed)



def log_received_speed(normalized_output_speed):
    """
    Logs the received speed to a text file.
    
    Parameters:
    normalized_output_speed (float): The normalized speed value to be logged.
    """
    log_file = "output_speed_log.txt"  # Name of the log file
    try:
        with open(log_file, "a") as file:
            file.write(f"Received speed: {normalized_output_speed}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value    
         

asyncio.run(main())
