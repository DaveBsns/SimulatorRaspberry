import asyncio
import json
import socket
import struct
import time
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

speed_queue = None
resistance_queue = None

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

async def write_resistance(client, characteristic):

    global resistance_queue
    global speed_queue

    while True:

        try:
            await client.start_notify(characteristic, notify_resistance_callback) # characteristic.uuid  
        except Exception as e:
            print("Error: ", e) 

        try:

            if (resistance_queue != None):


                #if (resistance_queue <=5):
                    #resistance_value = 0
                #else:
                resistance_value = (resistance_queue + 10) * 3.5
                resistance_value = min(resistance_value, 150)
                resistance_value = max(resistance_value, 0)
                resistance_queue = None
                
                resistance_value = int(resistance_value)
                print("write Resistance: ", resistance_value)
                await client.write_gatt_char(characteristic, bytearray([0x04, resistance_value]))
                await asyncio.sleep(0.25)

        except ValueError:
            print("Invalid input. Please enter a number between 1 and 100.")

        try:
            await client.stop_notify(characteristic.uuid)
        except Exception as e:
            print("Error: ", e) 


    
async def notify_speed_callback(sender, data):
    global resistance_queue
    global speed_queue
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
    #print(f"Received speed : {normalized_output_speed}")
    speed_queue = normalized_output_speed


def normalize_speed_value(value, min_val, max_val):
    range_val = max_val - min_val
    normalized_value = (value - min_val) / range_val
    return normalized_value

# Main async function: Manages connection and tasks
async def main_ble():

    global service_uuid
    global characteristic_resistance_uuid
    global characteristic_speed_uuid



    while True:
        try: 

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
                    write_task = asyncio.create_task(write_resistance(client=client, characteristic= CHARACTERISTIC_RESISTANCE))
                        #write_to_characteristic(client, CHARACTERISTIC_RESISTANCE))

                    try:
                        await write_task  # Keep the main function running
                    except asyncio.CancelledError:
                        # Stop notifications on exit
                        await client.stop_notify(CHARACTERISTIC_SPEED)
                        await write_task  # Ensure the write task ends
        except Exception: 
            time.sleep(3)
            print("Trying to connect again...")

# Run the main event loop
async def read_and_send_udp():

    UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.3"
    RECEIVE_FROM_MASTER_COLLECTOR_PORT = 2225

    global resistance_queue
    global speed_queue

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP_FROM_MASTER_COLLECTOR, RECEIVE_FROM_MASTER_COLLECTOR_PORT))
    udp_socket.setblocking(False)

    print("UDP socket is listening...")

    while True:
        # Reading from the UDP socket

        try:
            udp_incline_data = 0
            while True:
                try:
                    udp_incline_data, addr = udp_socket.recvfrom(47)
                    sender_ip, sender_port = addr
                    print(f"Received message: {udp_incline_data.decode()} from {sender_ip}:{sender_port}")
                    incline_value = json.loads(udp_incline_data.decode())
                    incline_value = int(incline_value["diretoResistance"])  
                    resistance_queue = incline_value
                except BlockingIOError:
                    break

        except BlockingIOError:
            time.sleep(0.01)  # 

        # Sending data if something is in the send_queue
        try:
            # Non-blocking get from the queue
            if (speed_queue != None):

                speed_to_send = speed_queue
                speed_queue = None
            
                udp_socket.sendto(str(speed_to_send).encode(), ("127.0.0.1", 1111))

        except asyncio.QueueEmpty:
            # Queue is empty, nothing to send
            pass

        await asyncio.sleep(0.1)  


async def main():
    await asyncio.gather(
        main_ble(),
        read_and_send_udp(),
    )

# Run the main event loop
asyncio.run(main())
