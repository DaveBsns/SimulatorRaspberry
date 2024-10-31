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


write_resistance_queue = asyncio.Queue(maxsize=1)
send_speed_queue = asyncio.Queue(maxsize=1)

current_resistance_value = 10.0
current_speed_value = 0.0

speed_queue = None
resistance_queue = None

def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value

async def write_resistance(client, characteristic, resistance_value):

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

async def notify_resistance_callback(self, sender):
    pass


class BluetoothCallback:


    def __init__(self):
        self.current_speed_value = 0.0
        
    
    async def notify_speed_callback(self, sender, data):
        global speed_queue
        # Convert the byte data to the speed value
        #speed_value = int.from_bytes(data, byteorder='little')  # Adjust based on your data format


        if struct.pack("@h", 1) == struct.pack("<h", 1):
            data = data[::-1]  # Reverse the byte order if little-endian

        result = struct.unpack_from(">h", data, 2)[0]
        output = result * 0.01
        if output < 0:
            output = abs(output)

        normalized_output_speed = normalize_speed_value(output, 0.0, 2.5) # changed from 3.5 to 2.5 for a better scaling. change it back if the value range is too small
        

        if (self.current_speed_value != normalized_output_speed):
            self.current_speed_value = normalized_output_speed
           # asyncio.run_coroutine_threadsafe(send_speed_queue.put(speed_value), asyncio.get_event_loop())
            print("Received new speed from direto:", normalized_output_speed)
            #send_speed_queue.put_nowait(normalized_output_speed)
            #await put_latest(send_speed_queue, normalized_output_speed)
            speed_queue = normalized_output_speed

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

async def read_and_send_udp():

    global current_speed_value
    global current_resistance_value
    global resistance_queue
    global speed_queue

    current_resistance_value = 10.0
    # Create a non-blocking UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP_FROM_MASTER_COLLECTOR, RECEIVE_FROM_MASTER_COLLECTOR_PORT))
    udp_socket.setblocking(False)

    print("UDP socket is listening...")

    while True:
        # Reading from the UDP socket
        try:

            data = await asyncio.get_event_loop().sock_recv(udp_socket, 47)
            resistance_data = json.loads(data.decode())
            resistance_value = int(resistance_data["diretoResistance"])
            

            if (resistance_value != current_resistance_value):
                current_resistance_value = resistance_value
                print("New Resistance from UDP: " + str(resistance_value))
                #write_resistance_queue.put_nowait(resistance_value)
                #await put_latest(write_resistance_queue, resistance_value)
                resistance_queue = resistance_value
                #asyncio.run_coroutine_threadsafe(write_resistance_queue.put(resistance_value), asyncio.get_event_loop())

        except BlockingIOError:
            pass

        # Sending data if something is in the send_queue
        try:
            # Non-blocking get from the queue
            if (speed_queue != None):

                speed_to_send = speed_queue
                speed_queue = None
            
                #speed_to_send = send_speed_queue.get_nowait()
                print("Sending speed: " + str(speed_to_send))
                udp_socket.sendto(str(speed_to_send).encode(), ("127.0.0.1", 1111))

        except asyncio.QueueEmpty:
            # Queue is empty, nothing to send
            pass

        await asyncio.sleep(0.1)  

async def connect_and_listen():

    global device_name

    global service_uuid
    global SERVICE

    global characteristic_resistance_uuid
    global characteristic_speed_uuid

    global CHARACTERISTIC_RESISTANCE
    global CHARACTERISTIC_SPEED

    global current_resistance_value

    global resistance_queue

    stop_event = asyncio.Event()  

    bluetooth_callback = BluetoothCallback()

    # Scanning and printing for BLE devices
    def callback(device, advertising_data):
        global DEVICEID   
        # print(device)
        # print("Test direto")
        if(device.name == device_name):
            DEVICEID = device
            stop_event.set()
            
    # Stops the scanning event    
    async with BleakScanner(callback) as scanner:  
        await stop_event.wait()

    if(DEVICEID != ""):
        client_is_connected = False
        while(client_is_connected == False):

            try:
                async with BleakClient(DEVICEID, timeout=90) as client:
                    client_is_connected = True
                    print("Client connected to ", DEVICEID.name)
                    # print("Device ID ", DEVICEID)
                    for service in client.services:
                        
                        if (service.uuid == service_uuid):
                            SERVICE = service
            
                        if (SERVICE != ""):
                            for characteristic in SERVICE.characteristics:

                                #if ("notify" in characteristic.properties):
                                   #print(characteristic)

                                if("write" in characteristic.properties and characteristic.uuid == characteristic_resistance_uuid):
                                    CHARACTERISTIC_RESISTANCE = characteristic
                                    print("Characteristic resistance: ",CHARACTERISTIC_RESISTANCE)

                                if("notify" in characteristic.properties and characteristic.uuid == characteristic_speed_uuid):
                                    CHARACTERISTIC_SPEED = characteristic
                                    print("Characteristic speed: ",CHARACTERISTIC_SPEED)

                            
                            while True:

                                


                                await asyncio.gather(
                                    bleSpeedRead(client, CHARACTERISTIC_SPEED, bluetooth_callback.notify_speed_callback),
                                    bleWrite(client= client, CHARACTERISTIC_RESISTANCE= CHARACTERISTIC_RESISTANCE)
                                )

                                await asyncio.sleep(0.01)  

            except BleakError as e:
                print(f"Failed to connect/discover services of {DEVICEID.name}: {e}")

async def bleSpeedRead(client, CHARACTERISTIC_SPEED, callback):
    await client.start_notify(CHARACTERISTIC_SPEED, callback)

async def bleWrite(client, CHARACTERISTIC_RESISTANCE):
    global resistance_queue

    try:

        if (resistance_queue != None): 
            resistance_to_write = resistance_queue
            resistance_queue = None
            await write_resistance(client=client, characteristic= CHARACTERISTIC_RESISTANCE, resistance_value=resistance_to_write)

    except Exception:
        print(Exception)


async def main():
    await asyncio.gather(
        connect_and_listen(),
        read_and_send_udp(),
    )
    #await connect_and_listen()

# Run the main event loop
asyncio.run(main())