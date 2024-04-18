import asyncio
from bleak import BleakScanner, BleakClient, exc
import socket

DEVICE_NAME = "RIZER"       
DEVICE_UUID = "fc:12:65:28:cb:44"
DEVICE_ID = ""

SERVICE_UUID = "347b0001-7635-408b-8918-8ff3949ce592" # Rizer - read steering
SERVICE_TILT_UUID = "347b00207635408b89188ff3949ce592"
SERVICE = ""

CHARACTERISTICS_STEEING_UUID = "347b0030-7635-408b-8918-8ff3949ce592" # Rizer - read steering
CHARACTERISTIC_TILT_UUID = "347b00017635408b89188ff3949ce592" # write tilt


characteristics_steering = ""



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


    def send_steering_data_udp(self, steering_data):
        # Create a UDP socket
        # print(steering_data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send speed_data
            udp_socket.sendto(str(steering_data).encode(), (self.udp_ip, self.udp_port))

async def read_steering(client, characteristic):
    bluetooth_callback = BluetoothCallback()
    try:
        await client.start_notify(characteristic, bluetooth_callback.notify_steering_callback)
        await asyncio.sleep(10) # keeps the connection open for 10 seconds
        await client.stop_notify(characteristic.uuid) 
        # print("Test steering")                                    
    except Exception as e:
        print("Error: ", e)                                    



async def scan_and_connect_rizer():
    global DEVICE_NAME

    global SERVICE_UUID
    global SERVICE

    global CHARACTERISTICS_STEEING_UUID
    global characteristics_steering

    stop_event = asyncio.Event()  

    # Scanning and printing for BLE devices
    def callback(device, advertising_data):
        global DEVICE_ID   
        # print(device)
        # print("Test rizer")
        if(device.name == DEVICE_NAME):
            
            DEVICE_ID = device
            stop_event.set()
            
    # Stops the scanning event    
    async with BleakScanner(callback) as scanner:
        '''
        try:
            await stop_event.wait()
        except KeyboardInterrupt:
            print("Scanning stopped by user.")
            scanner.stop()
        '''
        await stop_event.wait()
    
    if(DEVICE_ID != ""):
        # Connecting to BLE Device
        client_is_connected = False
        while(client_is_connected == False):
            try:
                async with BleakClient(DEVICE_ID, timeout=90) as client:
                    client_is_connected = True
                    print("Client connected to ", DEVICE_ID.name)
                    # return True
                    # logger.info("Device ID ", device_id)
                    for service in client.services:
                        # print("service: ", service)
                        
                        if (service.uuid == SERVICE_UUID):
                                SERVICE = service
                                # print("[service uuid] ", SERVICE.uuid)
                                    
                        if (SERVICE != ""):
                            # print("SERVICE", SERVICE)
                            for characteristic in SERVICE.characteristics:
                                
                                if("notify" in characteristic.properties and characteristic.uuid == CHARACTERISTICS_STEEING_UUID):
                                    characteristics_steering = characteristic
                                    # print("CHARACTERISTIC: ", CHARACTERISTIC_STEERING, characteristic.properties)
                                
                                
                            while True:
                                await read_steering(client, characteristics_steering)      
            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {DEVICE_ID.name}: {e}")
                # Add additional error handling or logging as needed
                # raise 

asyncio.run(scan_and_connect_rizer())




