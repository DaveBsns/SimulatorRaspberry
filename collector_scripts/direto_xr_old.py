import asyncio
from bleak import BleakScanner, BleakClient, BleakError
import struct
import sys
import socket 
import json
import time

device_name = "DIRETO XR"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "00001826-0000-1000-8000-00805f9b34fb" # Direto XR
SERVICE = ""

characteristic_resistance_uuid = "00002ad9-0000-1000-8000-00805f9b34fb" # Write Resistance
characteristic_speed_uuid = "00002ad2-0000-1000-8000-00805f9b34fb"  # Read Speed

CHARACTERISTIC_RESISTANCE = ""
CHARACTERISTIC_SPEED = ""

UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.3"
RECEIVE_FROM_MASTER_COLLECTOR_PORT = 2225


class BluetoothCallback:
    def __init__(self):
        self.received_speed_data = 0  # Initialize with None or any default value
        self.udp_ip = "127.0.0.1" # Send the direto data to the master_collector.py script via UDP over localhost
        # self.udp_ip = "10.30.77.221" # Ip of the Bicycle Simulator Desktop PC
        # self.udp_ip = "192.168.9.184" # IP of the Raspberry Pi
        self.udp_port = 1111

    async def notify_resistance_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        # print(data)
        test = "123"
        
    
    async def notify_speed_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        if struct.pack("@h", 1) == struct.pack("<h", 1):
            data = data[::-1]  # Reverse the byte order if little-endian

        result = struct.unpack_from(">h", data, 2)[0]
        output = result * 0.01
        normalized_output = normalize_speed_value(output, 0.0, 2.5) # changed from 3.5 to 2.5 for a better scaling. change it back if the value range is too small

        if output < 0:
            output = abs(output)
        
        print("Normalized Direto Speed: ", normalized_output)
        self.received_speed_data = normalized_output
        return normalized_output
        #self.send_speed_data_udp(self.received_speed_data)

    
    def send_speed_data_udp(self, speed_data):
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send speed_data
            udp_socket.sendto(str(speed_data).encode(), (self.udp_ip, self.udp_port))
    

def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value

async def write_and_read(client, read_characteristic, write_characterisitc, resitance_value):

    bluetooth_callback = BluetoothCallback()

    try: 
        print("s")
        await client
    
    except Exception as e:
        print("Error read and write: ", e)

async def write_resistance(client, characteristic, resistance_value):
    bluetooth_callback = BluetoothCallback()
    try:
        await client.start_notify(characteristic, bluetooth_callback.notify_resistance_callback) # characteristic.uuid  
    except Exception as e:
        print("Error: ", e) 
    # resistance_input = input("Enter a value between 1-100 to set the resistance level. (or 'x' to exit): ")
    resistance_value = int(resistance_value)
    try:
        #if 1 <= resistance_value <= 100:
        resistance_value = min(resistance_value, 100)
        resistance_value = max(resistance_value, 0)
        print("write Resistance: ", resistance_value)
        await client.write_gatt_char(characteristic, bytearray([0x04, resistance_value]))
       # elif resistance_value.lower() == 'x':
        #    await client.stop_notify(characteristic) # characteristic.uuid
       #     await asyncio.sleep(1)
       #     sys.exit()
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 100.")


    # print("Test resistance")
    

async def read_speed(client, characteristic):

    print("Reading...")

    bluetooth_callback = BluetoothCallback()
    try:
        # await asyncio.sleep(0.5)
        output = await client.start_notify(characteristic, bluetooth_callback.notify_speed_callback)
        await asyncio.sleep(0.01) # keeps the connection open for 10 seconds
        await client.stop_notify(characteristic.uuid) 
        return output
        # print("Test speed")                              

    except Exception as e:
        print("Error: ", e)
    


DEVICEID = ""
CHARACTERISTIC_RESISTANCE = None
CHARACTERISTIC_SPEED = None

async def scan_for_device():
    global DEVICEID
    stop_event = asyncio.Event()

    def callback(device, advertising_data):
        global DEVICEID
        if device.name == device_name:
            DEVICEID = device
            stop_event.set()

    async with BleakScanner(callback) as scanner:
        await stop_event.wait()

async def connect_to_ble_and_listen(queue):
    global CHARACTERISTIC_RESISTANCE, CHARACTERISTIC_SPEED
    async with BleakClient(DEVICEID, timeout=90) as client:
        print("Connected to", DEVICEID.name)
        service = client.services.get_service(service_uuid)

        for characteristic in service.characteristics:
            if "write" in characteristic.properties and characteristic.uuid == characteristic_resistance_uuid:
                CHARACTERISTIC_RESISTANCE = characteristic
                print("Characteristic resistance:", CHARACTERISTIC_RESISTANCE)

            if "notify" in characteristic.properties and characteristic.uuid == characteristic_speed_uuid:
                CHARACTERISTIC_SPEED = characteristic
                print("Characteristic speed:", CHARACTERISTIC_SPEED)

        while True:
            # Check for data in the queue and write it to the BLE device
            try:
                resistance_value = queue.get_nowait()
                if CHARACTERISTIC_RESISTANCE:
                    #await client.write_gatt_char(CHARACTERISTIC_RESISTANCE, resistance_value)
                    await write_resistance(client, CHARACTERISTIC_RESISTANCE, resistance_value)
                    print("Wrote resistance value:", resistance_value)

            except asyncio.QueueEmpty:
                pass

            await asyncio.sleep(0.01)  # Adjust sleep to prevent busy-waiting

async def listen_for_udp(queue):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP_FROM_MASTER_COLLECTOR, RECEIVE_FROM_MASTER_COLLECTOR_PORT))
    udp_socket.setblocking(False)
    print("Listening for UDP data...")

    while True:
        try:
            data = await asyncio.get_event_loop().sock_recv(udp_socket, 47)
            resistance_data = json.loads(data.decode())
            resistance_value = int(resistance_data["diretoResistance"])
            await queue.put(resistance_value)  # Send data to the BLE writing queue

        except BlockingIOError:
            await asyncio.sleep(0.01)  # Adjust sleep as needed for your application

async def main():

    await scan_for_device()

    if DEVICEID:
        queue = asyncio.Queue()
        await asyncio.gather(
            connect_to_ble_and_listen(queue),
            listen_for_udp(queue),
            #read(),
        )


async def read(): 
    global CHARACTERISTIC_RESISTANCE, CHARACTERISTIC_SPEED
    async with BleakClient(DEVICEID, timeout=90) as client:
        print("Connected to", DEVICEID.name)
        service = client.services.get_service(service_uuid)

        for characteristic in service.characteristics:
            if "write" in characteristic.properties and characteristic.uuid == characteristic_resistance_uuid:
                CHARACTERISTIC_RESISTANCE = characteristic
                print("Characteristic resistance:", CHARACTERISTIC_RESISTANCE)

            if "notify" in characteristic.properties and characteristic.uuid == characteristic_speed_uuid:
                CHARACTERISTIC_SPEED = characteristic
                print("Characteristic speed:", CHARACTERISTIC_SPEED)

        while True:
            # Check for data in the queue and write it to the BLE device
            try:
                await read_speed(client, CHARACTERISTIC_SPEED)

            except asyncio.QueueEmpty:
                pass

            

            await asyncio.sleep(0.01)  #

                            
asyncio.run(main())

