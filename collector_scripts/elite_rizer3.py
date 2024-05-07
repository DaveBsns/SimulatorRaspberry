import asyncio
from bleak import BleakClient, exc
import socket
import time
from master_collector import DataReceiver

tilt_received = 0       #received tilt data form UDP. Ready to send over BLE
steering_received = 0   #received steering data from RIZER. Ready to send over UDP
tilt_value = 0
current_tilt_value_on_razer = 0

class UDP_Handler:
    global tilt_value

    def __init__(self):
            self.received_steering_data = 0  # Initialize with None or any default value
            self.udp_ip = "127.0.0.1" # Send the rizer data to the master_collector.py script via UDP over localhost
            self.udp_port = 2222
            print("udp handler started")

    async def main(self):
        receiver = DataReceiver()
        while(True):
            if (steering_received == 1):
                self.send_steering_data_udp(self.steering_data)
            try:
                self.listening_udp()
                tilt_value = receiver.get_tilt()
                self.check_new_tilt(tilt_value)

            except Exception as e:
                print("Error: ", e)
    
    #send steering data over udp
    def send_steering_data_udp(self, steering_data):
        # Create a UDP socket
        print(steering_data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send speed_data
            udp_socket.sendto(str(steering_data).encode(), (self.udp_ip, self.udp_port))

    def listening_udp(self, udp_tilt_data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.listen(str(udp_tilt_data).encode(), (self.udp_ip, self.udp_port))
            print("Hello: ", udp_tilt_data)
    
    # check if the value of the tilt in unity is the same as on the rizer (currently not possible to check the value. just to store the changes)
    def check_new_tilt(self, udp_tilt_value):
        print("check new tilt")
        global tilt_received
        global tilt_value
        print("RIZER tilt: ", udp_tilt_value)
        if tilt_value != udp_tilt_value:
            tilt_value = udp_tilt_value
            tilt_received = 1

class BLE_Handler:
    #BLE constant
    DEVICE_NAME = "RIZER"       
    DEVICE_UUID = "fc:12:65:28:cb:44"

    SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592"           # Rizer - read steering
    SERVICE_TILT_UUID = "347b0001-7635-408b-8918-8ff3949ce592"

    INCREASE_TILT_HEX = "060102"
    DECREASE_TILT_HEX = "060402"

    CHARACTERISTICS_STEERING_UUID = "347b0030-7635-408b-8918-8ff3949ce592"   # Rizer - read steering
    CHARACTERISTIC_TILT_UUID = "347b0020-7635-408b-8918-8ff3949ce592"       # write tilt

    global steering_characteristics
    global tilt_characteristics

    global steering_service
    global tilt_service

    global current_tilt_value_on_razer
    
    async def read_and_ride_rizer(self, client):
        while(True):
            await self.read_steering(client, steering_characteristics)
            await self.write_tilt(client)
            print(tilt_characteristics)


    async def read_steering(self, client, characteristic):
        try:
            await client.start_notify(characteristic, self.notify_steering_callback)
            # await asyncio.sleep(10) # keeps the connection open for 10 seconds
            await client.stop_notify(characteristic.uuid)                                  
        except Exception as e:
            print("Error: ", e)                    

    async def write_tilt(self, client):
        global tilt_received
        try:
            await client.write_gatt_char(self.CHARACTERISTIC_TILT_UUID, bytes.fromhex(self.INCREASE_TILT_HEX), response=True)
            current_tilt_value_on_razer += 0.5
            tilt_received = 0
        except Exception as e:
            print("Error: ", e) 

    async def notify_steering_callback(self, sender, data):
        data = bytearray(data)
        steering = 0.0
        
        if data[3] == 65:
            steering = 1.0
        elif data[3] == 193:
            steering = -1.0
        
        self.received_steering_data = steering
        print(self.received_steering_data)

        udp.send_steering_data_udp(self.received_steering_data)


    async def main(self):
        global steering_characteristics
        global tilt_characteristics

        global steering_service
        global tilt_service

        global stering_ready                    #connection to steering BLE service ready
        global tilt_ready                       #connection to tilt BLE service ready
        
        # Connecting to BLE Device
        client_is_connected = False
        while(client_is_connected == False):
            try:
                async with BleakClient(self.DEVICE_UUID, timeout=90) as client:
                    client_is_connected = True
                    print("Client connected to ", self.DEVICE_UUID)
                    for service in client.services:
                        if (service.uuid == self.SERVICE_STEERING_UUID):
                            steering_service = service
                            print("[service uuid] ", steering_service.uuid)

                            if (steering_service != ""):
                                # print("SERVICE", SERVICE)
                                for characteristic in steering_service.characteristics:
                                    
                                    if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTICS_STEERING_UUID):
                                        steering_characteristics = characteristic
                                        # print("CHARACTERISTIC: ", CHARACTERISTIC_STEERING, characteristic.properties)
                                    print("IF")

                            print(stering_ready)
                            stering_ready = 1 

                        if (service.uuid == self.SERVICE_TILT_UUID):
                            tilt_service = service
                            print("[service uuid] ", tilt_service.uuid)

                            if (tilt_service != ""):
                                for characteristic in tilt_service.characteristics:

                                    print("characteristics UUID: ", characteristic.uuid)
                                    if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTIC_TILT_UUID):
                                        tilt_characteristics = characteristic
                            print(tilt_ready)
                            tilt_ready = 1

                    if (stering_ready == 1 and tilt_ready == 1):
                        print("all ready!")
                        self.read_and_ride_rizer()

            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {self.DEVICE_UUID}: {e}")
                # Add additional error handling or logging as needed
                # raise

async def main():
    udp_handler_task = asyncio.create_task(udp.main())
    ble_handler_task = asyncio.create_task(ble.main())

    await asyncio.gather(udp_handler_task, ble_handler_task)

# Creating instances of handlers
udp = UDP_Handler()                
ble = BLE_Handler()
print("asyncio start")
asyncio.run(main())