import asyncio
from bleak import BleakScanner, BleakClient

device_name = "RIZER"
DEVICEID = ""

service_uuid = "347b0001-7635-408b-8918-8ff3949ce592" # Rizer - read steering
SERVICE = ""

characteristic_steering_uuid = "347b0030-7635-408b-8918-8ff3949ce592" # Rizer - read steering
CHARACTERISTIC_STEERING = ""


class BluetoothCallback:
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

    async def notify_steering_callback(self, sender, data):
        data = bytearray(data)
        steering = 0.0
        
        if data[3] == 65:
            steering = 1.0
        elif data[3] == 193:
            steering = -1.0
        
        self.received_data = steering
        print(steering)

async def read_steering(client, characteristic):
    bluetooth_callback = BluetoothCallback()
    try:
        await client.start_notify(characteristic, bluetooth_callback.notify_steering_callback)
        # await asyncio.sleep(10) # keeps the connection open for 10 seconds
        # await client.stop_notify(characteristic.uuid) 
        # print("Test steering")                                    
    except Exception as e:
        print("Error: ", e)                                    



async def scan_and_connect():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_steering_uuid
    global CHARACTERISTIC_STEERING

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
        async with BleakClient(DEVICEID, timeout=120) as client:
            # logger.info("Device ID ", device_id)
            for service in client.services:
                # print("service: ", service.properties)
                
                if (service.uuid == service_uuid):
                        SERVICE = service
                        # print("[service uuid] ", SERVICE.uuid)
                            
                if (SERVICE != ""):
                    # print("SERVICE", SERVICE)
                    for characteristic in SERVICE.characteristics:
                        
                        if("notify" in characteristic.properties and characteristic.uuid == characteristic_steering_uuid):
                            CHARACTERISTIC_STEERING = characteristic
                            #print("CHARACTERISTIC: ", CHARACTERISTIC_STEERING, characteristic.properties)
                        
                        
                    while True:
                        await read_steering(client, CHARACTERISTIC_STEERING)
                           
                                     
asyncio.run(scan_and_connect())



