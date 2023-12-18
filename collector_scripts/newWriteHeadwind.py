import asyncio
from bleak import BleakScanner, BleakClient
import struct

device_name = "HEADWIND BC55"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "a026ee0c-0a7d-4ab3-97fa-f1500f9feb8b"
# SERVICE = ""

characteristic_uuid = "a026e038-0a7d-4ab3-97fa-f1500f9feb8b" 
# CHARACTERISTIC = ""

async def scan_and_connect():
    global device_name

    global service_uuid
    # global SERVICE

    global characteristic_uuid
    # global CHARACTERISTIC

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
        while True:
            await connect_to_device(DEVICEID, service_uuid, characteristic_uuid)
            # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 50])) # working if the fan is turned on and the script starting again

            # print("CLIENT CONNETION: ", client.is_connected, " ######################################################################################")
            # await device_client.disconnect()
            # print("client connection: ", device_client.is_connected)
                               
                               




async def connect_to_device(DEVICEID, service_uuid, characteristic_uuid, fan_speed):  # fan_speed is an integer between 0-100, 0 is off, 1 is on, and every other value adjust the fan_speed
        SERVICE = ""
        CHARACTERISTIC = ""

        async with BleakClient(DEVICEID, timeout=60) as client:
            print("Device ID ", DEVICEID)
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
                            '''
                            if ("write-without-response" in characteristic.properties):
                                # while True:
                                print("Type CHARACTERISTIC: ", type(CHARACTERISTIC))
                                await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04])) # Turns fan on -> bytearray([0x04, 0x04]), Turns fan off -> bytearray([0x04, 0x01]), Adjust fan Speed -> bytearray([0x02, <Decimalvalue between 1 and 100>])
                                print("client connection: ", client.is_connected)
                                # await client.disconnect()
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 100]))

                                '''
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 50])) # working if the fan is turned on and the script starting again
                            while True:
                                speed_input = input("Enter a value between 1-100 to set the fan speed. Enter 0 to turn off the fan (or 'x' to exit): ")
                                if speed_input.lower() == 'x':
                                    break
                                try:
                                    speed_value = int(speed_input)
                                    if 1 <= speed_value <= 100:
                                        # Convert speed value to byte and write to characteristic
                                        await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, speed_value]))
                                        print(f"Fan speed set to {speed_value}")
                                    elif speed_value == 0:
                                        await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x01]))
                                    else:
                                        print("Speed value should be between 1 and 100.")
                                except ValueError:
                                    print("Invalid input. Please enter a number between 1 and 100.")
                            
                            # print("CLIENT CONNETION: ", client.is_connected, " ######################################################################################")



asyncio.run(scan_and_connect())