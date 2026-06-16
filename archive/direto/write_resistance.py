import asyncio
from bleak import BleakScanner, BleakClient

class BluetoothCallback:
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

    async def notify_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        print(data)


device_name = "DIRETO XR"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "00001826-0000-1000-8000-00805f9b34fb" # Direto XR
SERVICE = ""

characteristic_uuid = "00002ad9-0000-1000-8000-00805f9b34fb" # Direto XR
CHARACTERISTIC = ""

async def scan_and_connect():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_uuid
    global CHARACTERISTIC

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
                        
                        if(characteristic.uuid == characteristic_uuid):
                            CHARACTERISTIC = characteristic

                            bluetooth_callback = BluetoothCallback()
                            while True:
                                try:
                                    await client.start_notify(CHARACTERISTIC, bluetooth_callback.notify_callback) # characteristic.uuid  
                                except Exception as e:
                                    print("Error: ", e) 
                                resistance_input = input("Enter a value between 1-100 to set the resistance level. (or 'x' to exit): ")
                                resistance_value = int(resistance_input)
                                try:
                                    if 1 <= resistance_value <= 100:
                                            await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, resistance_value]))
                                    elif resistance_input.lower() == 'x':
                                        await client.stop_notify(CHARACTERISTIC) # characteristic.uuid
                                        await asyncio.sleep(1)
                                        break
                                except ValueError:
                                    print("Invalid input. Please enter a number between 1 and 100.")

asyncio.run(scan_and_connect())