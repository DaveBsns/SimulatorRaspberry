import asyncio
from bleak import BleakScanner, BleakClient
import struct
import sys


device_name = "DIRETO XR"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "00001826-0000-1000-8000-00805f9b34fb" # Direto XR
SERVICE = ""

characteristic_resistance_uuid = "00002ad9-0000-1000-8000-00805f9b34fb" # Write Resistance
characteristic_speed_uuid = "00002ad2-0000-1000-8000-00805f9b34fb"  # Read Speed


CHARACTERISTIC_RESISTANCE = ""
CHARACTERISTIC_SPEED = ""


class BluetoothCallback:
    def __init__(self):
        self.received_speed_data = 0  # Initialize with None or any default value

    async def notify_resistance_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        print(data)
    
    async def notify_speed_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        if struct.pack("@h", 1) == struct.pack("<h", 1):
            data = data[::-1]  # Reverse the byte order if little-endian

        result = struct.unpack_from(">h", data, 2)[0]
        output = result * 0.01
        normalized_output = normalize_speed_value(output, 0.0, 3.5)

        if output < 0:
            output = abs(output)
        print(normalized_output)

        self.received_speed_data = normalized_output

def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value


async def write_resistance(client, characteristic):
    bluetooth_callback = BluetoothCallback()
    try:
        await client.start_notify(characteristic, bluetooth_callback.notify_resistance_callback) # characteristic.uuid  
    except Exception as e:
        print("Error: ", e) 
    resistance_input = input("Enter a value between 1-100 to set the resistance level. (or 'x' to exit): ")
    resistance_value = int(resistance_input)
    try:
        if 1 <= resistance_value <= 100:
            await client.write_gatt_char(characteristic, bytearray([0x04, resistance_value]))
        elif resistance_input.lower() == 'x':
            await client.stop_notify(characteristic) # characteristic.uuid
            await asyncio.sleep(1)
            sys.exit()
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 100.")
    # print("Test resistance")
    

async def read_speed(client, characteristic):
    bluetooth_callback = BluetoothCallback()
    try:
        await client.start_notify(characteristic, bluetooth_callback.notify_speed_callback)
        # await asyncio.sleep(0.25) # keeps the connection open for 10 seconds
        # await client.stop_notify(characteristic) 
        # print("Test speed")                                    

    except Exception as e:
        print("Error: ", e)
    


async def scan_and_connect():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_resistance_uuid
    global characteristic_speed_uuid

    global CHARACTERISTIC_RESISTANCE
    global CHARACTERISTIC_SPEED

    stop_event = asyncio.Event()  

    # Scanning and printing for BLE devices
    def callback(device, advertising_data):
        global DEVICEID   
        print(device)
        if(device.name == device_name):
            DEVICEID = device
            stop_event.set()
            
    # Stops the scanning event    
    async with BleakScanner(callback) as scanner:
        await stop_event.wait()
    
    if(DEVICEID != ""):
        # Connecting to BLE Device
        async with BleakClient(DEVICEID, timeout=60) as client:
            print("Device ID ", DEVICEID)
            for service in client.services:
                 
                if (service.uuid == service_uuid):
                        SERVICE = service
     
                if (SERVICE != ""):
                    for characteristic in SERVICE.characteristics:
                        if("write" in characteristic.properties and characteristic.uuid == characteristic_resistance_uuid):
                            CHARACTERISTIC_RESISTANCE = characteristic
                            print("Characteristic resistance: ",CHARACTERISTIC_RESISTANCE)

                        if("notify" in characteristic.properties and characteristic.uuid == characteristic_speed_uuid):
                            CHARACTERISTIC_SPEED = characteristic
                            print("Characteristic speed: ",CHARACTERISTIC_SPEED)

                    while True:
                        await write_resistance(client, CHARACTERISTIC_RESISTANCE)
                        await read_speed(client, CHARACTERISTIC_SPEED)

                            
asyncio.run(scan_and_connect())