import asyncio
from bleak import BleakClient, exc
import socket
import time
from master_collector import DataReceiver

DEVICE_NAME = "RIZER"       
DEVICE_UUID = "fc:12:65:28:cb:44"

SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592" # Rizer - read steering
SERVICE_TILT_UUID = "347b0001-7635-408b-8918-8ff3949ce592"


INCREASE_TILT_HEX = "060102"
DECREASE_TILT_HEX = "060402"

steering_service = ""
tilt_service = ""

stering_ready = 0
tilt_ready = 0

stored_tilt_value = 0


CHARACTERISTICS_STEEING_UUID = "347b0030-7635-408b-8918-8ff3949ce592" # Rizer - read steering
CHARACTERISTIC_TILT_UUID = "347b0020-7635-408b-8918-8ff3949ce592" # write tilt


steering_characteristics = ""
tilt_characteristics = ""


class BluetoothCallback:
    def __init__(self):
        self.received_steering_data = 0  # Initialize with None or any default value
        self.udp_ip = "127.0.0.1" # Send the rizer data to the master_collector.py script via UDP over localhost
        # self.udp_ip = "10.30.77.221" # Ip of the Bicycle Simulator Desktop PC
        # self.udp_ip = "192.168.9.184" # IP of the Raspberry Pi
        self.udp_port = 2222
        

    async def notify_steering_callback(self, sender, data):
        data = bytearray(data)
        steering = 0.0
        
        if data[3] == 65:
            steering = 1.0
        elif data[3] == 193:
            steering = -1.0
        
        self.received_steering_data = steering
        print(self.received_steering_data)

        self.send_steering_data_udp(self.received_steering_data)

    #send steering data over udp
    def send_steering_data_udp(self, steering_data):
        # Create a UDP socket
        # print(steering_data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send speed_data
            udp_socket.sendto(str(steering_data).encode(), (self.udp_ip, self.udp_port))

    def listening_udp(self, udp_tilt_data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.listen(str(udp_tilt_data).encode(), (self.udp_ip, self.udp_port))
            print("Hello: ", udp_tilt_data)

async def read_steering(client, characteristic):
    bluetooth_callback = BluetoothCallback()
    try:
        await client.start_notify(characteristic, bluetooth_callback.notify_steering_callback)
        await asyncio.sleep(10) # keeps the connection open for 10 seconds
        await client.stop_notify(characteristic.uuid) 
        # print("Test steering")                                    
    except Exception as e:
        print("Error: ", e)                    

async def write_tilt(client, characteristic):
    bluetooth_callback = BluetoothCallback()
    try:
        #TODO Write bt stuff
        print("BT stuff")
        await client.write_gatt_char(CHARACTERISTIC_TILT_UUID, bytes.fromhex(INCREASE_TILT_HEX), response=True)
        stored_tilt_value += 0.5
    except Exception as e:
        print("Error: ", e) 

# check if the value of the tilt in unity is the same as on the rizer (currently not possible to check the value. just to store the changes)
def get_new_tilt_value():
    try:
        receiver.start_udp_listener()
        tilt_value = receiver.get_tilt()
        print("RIZER tilt: ", tilt_value)
        if tilt_value != stored_tilt_value:
            stored_tilt_value = tilt_value

    except Exception as e:
        print("Error: ", e)
           

async def scan_and_connect_rizer():
    global DEVICE_NAME

    global SERVICE_STEERING_UUID

    global steering_service
    global tilt_service

    global CHARACTERISTICS_STEEING_UUID
    global steering_characteristics
    global tilt_characteristics

    global stering_ready
    global tilt_ready
    
    # Connecting to BLE Device
    client_is_connected = False
    while(client_is_connected == False):
        try:
            async with BleakClient(DEVICE_UUID, timeout=90) as client:
                client_is_connected = True
                #print("Client connected to ", DEVICE_ID.name)
                #print("Client connected to ", DEVICE_ID)
                print("Client connected to ", DEVICE_UUID)
                # return True
                # logger.info("Device ID ", device_id)
                for service in client.services:
                    # print("service: ", service)
                    
                    if (service.uuid == SERVICE_STEERING_UUID):
                        steering_service = service
                        print("[service uuid] ", steering_service.uuid)

                        if (steering_service != ""):
                            # print("SERVICE", SERVICE)
                            for characteristic in steering_service.characteristics:
                                
                                if("notify" in characteristic.properties and characteristic.uuid == CHARACTERISTICS_STEEING_UUID):
                                    steering_characteristics = characteristic
                                    # print("CHARACTERISTIC: ", CHARACTERISTIC_STEERING, characteristic.properties)
                                print("IF")

                        print(stering_ready)
                        stering_ready = 1 

                    if (service.uuid == SERVICE_TILT_UUID):
                        tilt_service = service
                        print("[service uuid] ", tilt_service.uuid)

                        if (tilt_service != ""):
                            for characteristic in tilt_service.characteristics:

                                print("characteristics UUID: ", characteristic.uuid)
                                if("notify" in characteristic.properties and characteristic.uuid == CHARACTERISTIC_TILT_UUID):
                                    tilt_characteristics = characteristic
                        print(tilt_ready)
                        tilt_ready = 1

                while (stering_ready == 1 and tilt_ready == 1):
                    print("all ready!")
                    await read_steering(client, steering_characteristics)
                    await write_tilt(client, tilt_characteristics)
                    print(tilt_characteristics)
                    print("read and write!")
 

        except exc.BleakError as e:
            print(f"Failed to connect/discover services of {DEVICE_UUID}: {e}")
            # Add additional error handling or logging as needed
            # raise 

asyncio.run(scan_and_connect_rizer())

'create UDP_Handler in own task'