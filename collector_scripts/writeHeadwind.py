import asyncio
from bleak import BleakScanner, BleakClient
import struct


class BluetoothCallback:
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

    async def notify_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        print(data)

        '''
        if struct.pack("@h", 1) == struct.pack("<h", 1):
            data = data[::-1]  # Reverse the byte order if little-endian

        result = struct.unpack_from(">h", data, 2)[0]
        output = result * 0.01

        if output < 0:
            output = abs(output)
        print(output)

        self.received_data = output
        '''


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

                            if ("write-without-response" in characteristic.properties):
                                # while True:
                                print("Type CHARACTERISTIC: ", type(CHARACTERISTIC))
                                await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04])) # Turns fan on -> bytearray([0x04, 0x04]), Turns fan off -> bytearray([0x04, 0x01]), Adjust fan Speed -> bytearray([0x02, <Decimalvalue between 1 and 100>])
                                print("client connection: ", client.is_connected)
                                # await client.disconnect()
                                # print("client connection: ", client.is_connected)
                                # await asyncio.sleep(10) # keeps the connection open for 10 seconds
                                # print("TIMER")
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 100]))
                                '''
                                if ("notify" in characteristic.properties):
                               
                                    bluetooth_callback = BluetoothCallback()
                                    while True:
                                        try:
                                            
                                            # value = await client.read_gatt_char(characteristic.uuid)
                                            # print("Die CHARARARA iSt: ", CHARACTERISTIC, CHARACTERISTIC.properties)
                                            # await client.start_notify(characteristic.uuid, on_notification)
                                            await client.start_notify(characteristic.uuid, bluetooth_callback.notify_callback)
                                            print("client connection: ", client.is_connected)
                                            await asyncio.sleep(10) # keeps the connection open for 10 seconds
                                            await client.stop_notify(characteristic.uuid)                                     
                                            
                                        except Exception as e:
                                            print("Error: ", e)
                                            # run_read_loop = False

                                '''
                                
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 50])) # working if the fan is turned on and the script starting again
                                while True:
                                    print("client connection: ", client.is_connected)
                                    await client.disconnect()
                                    print("client connection: ", client.is_connected)
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
                                # bluetooth_callback = BluetoothCallback()
                                

                                
                               

asyncio.run(scan_and_connect())


async def connect_to_device(DEVICEID, SERVICE):
    if(DEVICEID != ""):
        # Connecting to BLE Device
        # print("DEVICEID: ",DEVICEID.address)
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

                            if ("write-without-response" in characteristic.properties):
                                # while True:
                                print("Type CHARACTERISTIC: ", type(CHARACTERISTIC))
                                await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04])) # Turns fan on -> bytearray([0x04, 0x04]), Turns fan off -> bytearray([0x04, 0x01]), Adjust fan Speed -> bytearray([0x02, <Decimalvalue between 1 and 100>])
                                print("client connection: ", client.is_connected)
                                # await client.disconnect()
                                # print("client connection: ", client.is_connected)
                                # await asyncio.sleep(10) # keeps the connection open for 10 seconds
                                # print("TIMER")
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 100]))
                                '''
                                if ("notify" in characteristic.properties):
                               
                                    bluetooth_callback = BluetoothCallback()
                                    while True:
                                        try:
                                            
                                            # value = await client.read_gatt_char(characteristic.uuid)
                                            # print("Die CHARARARA iSt: ", CHARACTERISTIC, CHARACTERISTIC.properties)
                                            # await client.start_notify(characteristic.uuid, on_notification)
                                            await client.start_notify(characteristic.uuid, bluetooth_callback.notify_callback)
                                            print("client connection: ", client.is_connected)
                                            await asyncio.sleep(10) # keeps the connection open for 10 seconds
                                            await client.stop_notify(characteristic.uuid)                                     
                                            
                                        except Exception as e:
                                            print("Error: ", e)
                                            # run_read_loop = False

                                '''
                                
                                # await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, 50])) # working if the fan is turned on and the script starting again
                                while True:
                                    print("client connection: ", client.is_connected)
                                    await client.disconnect()
                                    print("client connection: ", client.is_connected)
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
                                # bluetooth_callback = BluetoothCallback()
