import asyncio
from bleak import BleakScanner, BleakClient
import struct


class BluetoothCallback:
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

    async def notify_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        if struct.pack("@h", 1) == struct.pack("<h", 1):
            data = data[::-1]  # Reverse the byte order if little-endian

        result = struct.unpack_from(">h", data, 2)[0]
        output = result * 0.01

        if output < 0:
            output = abs(output)
        print(output)

        self.received_data = output


device_name = "HEADWIND BC55"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "a026ee0c-0a7d-4ab3-97fa-f1500f9feb8b"
SERVICE = ""

characteristic_uuid = "a026e038-0a7d-4ab3-97fa-f1500f9feb8b" 
CHARACTERISTIC = ""

async def scan_and_connect():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_uuid
    global CHARACTERISTIC

    global value_to_write
    global old_value

    global is_first_entry
    global run_read_loop  

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
        # print("DEVICEID: ",DEVICEID.address)
        async with BleakClient(DEVICEID.address, timeout=120) as client:
            # logger.info("Device ID ", device_id)
            for service in client.services:
                # print("service: ", service)
                 
                if (service.uuid == service_uuid):
                        SERVICE = service
                        # print("[service uuid] ", SERVICE.uuid)
                            
                if (SERVICE != ""):
                    # print("SERVICE", SERVICE)
                    for characteristic in SERVICE.characteristics:
                        # if ("notify" in characteristic.properties):
                        # print("[Characteristic] %s", characteristic, characteristic.properties)
                        
                        if(characteristic.uuid == characteristic_uuid):
                            CHARACTERISTIC = characteristic
                            # print("CHARACTERISTIC: ", characteristic, characteristic.properties)

                            if ("write-without-response" in characteristic.properties):
                                await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04])) 
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 100])) # working if the fan is turned on and the script starting again
                                while True:
                                    speed_input = input("Enter a value between 1-100 to set the fan speed. Enter 0 to turn off the fan (or 'x' to exit): ")
                                    if speed_input.lower() == 'x':
                                        break
                                    try:
                                        speed_value = int(speed_input)
                                        if 1 <= speed_value <= 100:
                                            # Convert speed value to byte and write to characteristic
                                            await client.write_gatt_char(str(characteristic.uuid), bytearray([0x02]))
                                            await client.write_gatt_char(str(characteristic.uuid), bytearray([0x07]))
                                            print(f"Fan speed set to {speed_value}")
                                        elif speed_value == 0:
                                            await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04]))
                                        else:
                                            print("Speed value should be between 1 and 100.")
                                    except ValueError:
                                        print("Invalid input. Please enter a number between 1 and 100.")
                                # bluetooth_callback = BluetoothCallback()

                                
                               

asyncio.run(scan_and_connect())