import asyncio
import struct
from bleak import BleakClient, BleakScanner

# Replace with your device's MAC address and characteristic UUIDs
DEVICE_ADDRESS = "xx:xx:xx:xx:xx:xx"
CHARACTERISTIC_WRITE_UUID = "00002ad9-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_NOTIFY_UUID = "00002ad2-0000-1000-8000-00805f9b34fb"


device_name = "DIRETO XR"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "00001826-0000-1000-8000-00805f9b34fb" # Direto XR
SERVICE = ""

characteristic_resistance_uuid = "00002ad9-0000-1000-8000-00805f9b34fb" # Write Resistance
characteristic_speed_uuid = "00002ad2-0000-1000-8000-00805f9b34fb"  # Read Speed

CHARACTERISTIC_RESISTANCE = ""
CHARACTERISTIC_SPEED = ""

# Set Processing queues

async def find_device_by_name():
    global device_name
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    for device in devices:
        if device.name == device_name:
            print(f"Found device: {device.name} with MAC address: {device.address}")
            return device.address

    print("Device not found. Make sure it is in range and advertising.")
    return None

async def notify_resistance_callback(self, sender):
    pass

async def write_resistance(client, characteristic, resistance_value):

    while True:

        try:
            await client.start_notify(characteristic, notify_resistance_callback) # characteristic.uuid  
        except Exception as e:
            print("Error: ", e) 

        try:

            resistance_value = min(resistance_value, 100)
            resistance_value = max(resistance_value, 0)
            print("write Resistance: ", resistance_value)
            resistance_value = int(resistance_value)
            #resistance_value = 100 - resistance_value
            await client.write_gatt_char(characteristic, bytearray([0x04, resistance_value]))

        except ValueError:
            print("Invalid input. Please enter a number between 1 and 100.")

        try:
            await client.stop_notify(characteristic.uuid)
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
    print(f"Received speed : {normalized_output_speed}")

def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value

# Main async function: Manages connection and tasks
async def main():

    global service_uuid
    global characteristic_resistance_uuid
    global characteristic_speed_uuid

    DEVICE_ADDRESS = await find_device_by_name()
    SERVICE = ""
    CHARACTERISTIC_RESISTANCE = ""
    CHARACTERISTIC_SPEED = ""

    async with BleakClient(DEVICE_ADDRESS) as client:
        if not client.is_connected:
            print("Failed to connect to device.")
            return
        
        for service in client.services:

            if (service.uuid == service_uuid):
                SERVICE = service    

        if (SERVICE != ""):

            for characteristic in SERVICE.characteristics:

                if("write" in characteristic.properties and characteristic.uuid == characteristic_resistance_uuid):
                    CHARACTERISTIC_RESISTANCE = characteristic
                    print("Characteristic resistance: ",CHARACTERISTIC_RESISTANCE)
                    print(f"Properties of characteristic: {CHARACTERISTIC_RESISTANCE.properties}")


                if("notify" in characteristic.properties and characteristic.uuid == characteristic_speed_uuid):
                    CHARACTERISTIC_SPEED = characteristic
                    print("Characteristic speed: ",CHARACTERISTIC_SPEED)  
                    print(f"Properties of characteristic: {CHARACTERISTIC_SPEED.properties}")

            # Start receiving notifications
            await client.start_notify(CHARACTERISTIC_SPEED, notify_speed_callback)

            # Run the write task concurrently
            write_task = asyncio.create_task(write_resistance(client=client, characteristic= CHARACTERISTIC_RESISTANCE, resistance_value= 10))
                #write_to_characteristic(client, CHARACTERISTIC_RESISTANCE))

            try:
                await write_task  # Keep the main function running
            except asyncio.CancelledError:
                # Stop notifications on exit
                await client.stop_notify(CHARACTERISTIC_SPEED)
                await write_task  # Ensure the write task ends

# Run the main event loop
asyncio.run(main())
