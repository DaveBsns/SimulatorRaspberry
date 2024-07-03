import asyncio
from bleak import BleakScanner, BleakClient, exc
from master_collector import DataReceiver
import socket
import json
import select
import time

class BluetoothCallback():
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

    async def notify_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        # print(data)
        test = "123"


device_name = "HEADWIND BC55"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "a026ee0c-0a7d-4ab3-97fa-f1500f9feb8b"
SERVICE = ""

characteristic_uuid = "a026e038-0a7d-4ab3-97fa-f1500f9feb8b" 
CHARACTERISTIC = ""

UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.3"
RECEIVE_FROM_MASTER_COLLECTOR_PORT = 2224

async def scan_and_connect_headwind():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_uuid
    global CHARACTERISTIC

    global value_to_write
    global old_value

    global is_first_entry
    global run_read_loop 

    speed_value = 0 

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
        # new 
        try:
            await stop_event.wait()
        except KeyboardInterrupt:
            print("Scanning stopped by user.")
            scanner.stop()
        # new end    
        # old############
        await stop_event.wait()
        # old############
    
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
                                
                                if(characteristic.uuid == characteristic_uuid):
                                    CHARACTERISTIC = characteristic

                                    #receiver = DataReceiver()
                                    #print("rizer id: ", id(receiver))
                                    
                                    bluetooth_callback = BluetoothCallback()
                                    #receiver.open_udp_socket()
                                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                                        udp_socket.bind((UDP_IP_FROM_MASTER_COLLECTOR, RECEIVE_FROM_MASTER_COLLECTOR_PORT))
                                        udp_socket.setblocking(False)                                                                   #without this flag it waits until it gets data
                                        while True:
                                            try:
                                                ble_fan_data, addr = udp_socket.recvfrom(1024)                                          # Buffer size is 1024 bytes
                                                sender_ip, sender_port = addr                                                           # Extract the sender's IP and port from addr
                                                print(f"Received message: {ble_fan_data.decode()} from {sender_ip}:{sender_port}")
                                                print("ble fan data: ", ble_fan_data)
                                                ble_fan_value = json.loads(ble_fan_data.decode())
                                                print("decoded fan value ", ble_fan_value)
                                                speed_value = int(ble_fan_value["fanSpeed"])
                                                 
                                                print("ble_fan_value: ", ble_fan_value)
                                                print("value: ", speed_value)
                                            except BlockingIOError:
                                                time.sleep(0.01)  # Small sleep to prevent busy-waiting
                                            except Exception as e:
                                                print("Error: ", e)
                                            try:
                                                await client.start_notify(CHARACTERISTIC, bluetooth_callback.notify_callback) # characteristic.uuid  
                                            except Exception as e:
                                                print("Error: ", e)

                                            try:
                                                if 2 <= speed_value <= 100:     #TODO we have to write 1 before we can write some other values
                                                    await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, speed_value]))
                                                    print(f"Fan speed set to {speed_value}")
                                                elif speed_value == 1:
                                                    await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04])) # Turns fan on -> bytearray([0x04, 0x04]), Turns fan off -> bytearray([0x04, 0x01]), Adjust fan Speed -> bytearray([0x02, <Decimalvalue between 1 and 100>])
                                                elif speed_value == 0:
                                                    await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x01]))
                                                else:
                                                    print("Speed value should be between 1 and 100.")
                                            except ValueError:
                                                print("Invalid input. Please enter a number between 1 and 100.")
                                            
            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {DEVICEID.name}: {e}")
                # Add additional error handling or logging as needed
                # raise  

try:
    asyncio.run(scan_and_connect_headwind())
except BaseException:
    import sys
    print(sys.exc_info()[0])
    import traceback
    print(traceback.format_exc())
finally:
    print("Press Enter to continue ...")
    input()

