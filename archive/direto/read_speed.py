import asyncio
from bleak import BleakScanner, BleakClient
import struct

class BluetoothCallback:
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

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

        self.received_data = normalized_output


device_name = "DIRETO XR"
DEVICEID = ""

service_uuid = "00001826-0000-1000-8000-00805f9b34fb" # Direto - Fitness Machine Service
SERVICE = ""

characteristic_uuid = "00002ad2-0000-1000-8000-00805f9b34fb" # Direto
CHARACTERISTIC = ""

value_to_write = ""
old_value = ""

def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value

'''
async def on_notification(sender, data):
    # collection = db["sensor_values"]  # Sammlungsname // outsourcen zur api
    # data = data[0]
    # value = data.decode('utf-8')

    # Daten in die MongoDB schreiben
    # entry = {"value": value}
    # integer_value = int.from_bytes(data, byteorder='big') 
    #collection.insert_one(entry)
    # print(f"Data written to MongoDB: {entry}")
    # print(f"Data written to MongoDB: {data}")
    if struct.pack("@h", 1) == struct.pack("<h", 1):
        data = data[::-1]  # Reverse the byte order if little-endian

    result = struct.unpack_from(">h", data, 2)[0]
    output = result * 0.01
    normalized_output = normalize_speed_value(output, 0.0, 3.5)

    if output < 0:
        output = abs(output)
    print(normalized_output)
'''
'''
    if (value[6] != value_to_write):
        value_to_write = value[6]
        if(entry_id == None):
            write_in_db(value_to_write)
            entry_id = await get_id()
            #print("Entry ID: "+entry_id)
            #message = value_to_write
            print("Test", value_to_write)
            # is_first_entry = False
        else:
            #message = value_to_write
            print(value_to_write)
            # await update_in_db(entry_id, value_to_write)
            write_in_db(value_to_write)
            logger.info("Updateing for id: %r ....With Value %r", entry_id, value_to_write)
            #print("Updateing for id: ", entry_id, "....With Value ", value_to_write)
            # print("old value: ", old_value)
    
        
    old_value = value_to_write
    logger.info(
        "  [Characteristic] %s (%s), Value: %r",
        characteristic,
        ",".join(characteristic.properties) ,
        # value[0],
    )
'''

async def scan_and_connect():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_uuid
    global CHARACTERISTIC

    global value_to_write
    global old_value

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
                        print("[service uuid] ", SERVICE.uuid)
                            
                if (SERVICE != ""):
                    # print("SERVICE", SERVICE)
                    for characteristic in SERVICE.characteristics:
                        # if ("notify" in characteristic.properties):
                        print("[Characteristic] %s", characteristic, characteristic.properties)
                        
                        if(characteristic.uuid == characteristic_uuid):
                            CHARACTERISTIC = characteristic
                            print("CHARACTERISTIC: ", characteristic, characteristic.properties)
                            if ("notify" in characteristic.properties):
                                bluetooth_callback = BluetoothCallback()

                                while True:
                                    try:
                                        await client.start_notify(characteristic.uuid, bluetooth_callback.notify_speed_callback)
                                        await asyncio.sleep(10) # keeps the connection open for 10 seconds
                                        await client.stop_notify(characteristic.uuid)                                     
                           
                                    except Exception as e:
                                        print("Error: ", e)                                    
asyncio.run(scan_and_connect())



