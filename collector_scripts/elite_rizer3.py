import asyncio
from bleak import BleakClient, exc
import socket
import time
from master_collector import DataReceiver

#global variables
tilt_received = 0                           #received tilt data form UDP. Ready to send over BLE
steering_received = 0                       #received steering data from RIZER. Ready to send over UDP
tilt_value = None
current_tilt_value_on_razer = None          #received tilt data form UDP. Ready to send over BLE
client = None


class UDP_Handler:

    def __init__(self):
        global tilt_value
        global tilt_received

        tilt_value = 0
        tilt_received = 0
        self.received_steering_data = 0  # Initialize with None or any default value
        self.udp_ip = "127.0.0.1" # Send the rizer data to the master_collector.py script via UDP over localhost
        self.udp_port = 2222
        print("udp handler started")
            

    async def main(self):
        global tilt_value
        global steering_received
        receiver = DataReceiver()
        self.steering_data = None
        steering_received = None
        while(True):
            await asyncio.sleep(1)
            print("udp main")
            if (steering_received == 1):                            #when steering value has chanched, send it to unity
                await self.send_steering_data_udp(self.steering_data)
            try:
                #self.listening_udp                 maybe not needed
                tilt_value = receiver.get_tilt()                    #read tilt from unity
                self.check_new_tilt(tilt_value)                     #check if tilt value has changed or is still the same

            except Exception as e:
                print("Error: ", e)
    
    def set_tilt_received(received):
        tilt_received = received
    
    def get_til_received():
        return tilt_received

    #send steering data over udp
    def send_steering_data_udp(self, steering_data):
        # Create a UDP socket
        print(steering_data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send speed_data
            udp_socket.sendto(str(steering_data).encode(), (self.udp_ip, self.udp_port))

    def listening_udp(self):
        udp_tilt_data = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.listen(str(udp_tilt_data).encode(), (self.udp_ip, self.udp_port))
            print("Hello: ", udp_tilt_data)
    
    # check if the value of the tilt in unity is the same as on the rizer (currently not possible to check the value. just to store the changes)
    def check_new_tilt(self, udp_tilt_value):
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

    global current_tilt_value_on_razer                          # current position of RIZER (save ervery change for verification)
    
    async def read_and_ride_rizer(self):
        global tilt_received
        global client
        print("read and write")
        while(True):
            if (self.init_ack == True):
                await self.read_steering()
                #self.read_steering(client, steering_characteristics)
                print("read steering rizer")
                if (tilt_received == 1):
                    await self.write_tilt(client)
                    tilt_received = 0
                    print("tilt writed")
            else:
                print("wait init ack")


    async def read_steering(self):
        data = bytearray(8)
        sender = 0
        await asyncio.sleep(1)
        print("read steering")
        try:
            print("should reading...")
            await client.start_notify(self.steering_characteristics, self.notify_steering_callback(sender, data))
            # Access the notification data using data argument
            print(f"Steering data: {sender}")
            print(f"Steering data: {data}")
            await asyncio.sleep(1) # keeps the connection open for 10 seconds
            print("test here")
            await client.stop_notify(self.steering_characteristics.uuid)                                  
        except Exception as e:
            print("Error: ", e)                    

    async def write_tilt(self):
        global client
        global tilt_received
        try:
            await client.write_gatt_char(self.CHARACTERISTIC_TILT_UUID, bytes.fromhex(self.INCREASE_TILT_HEX), response=True)
            current_tilt_value_on_razer += 0.5
            tilt_received = 0
        except Exception as e:
            print("Error: ", e) 

    def notify_steering_callback(data):
        print("notify steering")
        data = bytearray(data)
        steering = 0.0
        
        if data[3] == 65:
            steering = 1.0
        elif data[3] == 193:
            steering = -1.0
        
        self.received_steering_data = steering
        print(self.received_steering_data)
        udp.send_steering_data_udp(self.received_steering_data)


    def __init__(self):
        global steering_characteristics
        global tilt_characteristics

        global steering_service
        global tilt_service

        #global steering_ready                   #connection to steering BLE service ready
        #global tilt_ready                       #connection to tilt BLE service ready

        global client_is_connected
        global client_is_connected
        
        # Connecting to BLE Device
        print("Connecting to BLE Device")
        client_is_connected = False
        self.steering_ready = 0
        self.tilt_ready = 0
        self.tilt_received = 0
        self.steering_characteristics = None
        self.tilt_characteristics = 0
        self.init_ack = False

    async def async_init(self):
        global client
        global client_is_connected
        print("start async init")
        while not client_is_connected:
            try:
                client = BleakClient(self.DEVICE_UUID, timeout=90)
                await client.connect()
                client_is_connected = True
                print("Client connected to ", self.DEVICE_UUID)
                for service in client.services:
                    if (service.uuid == self.SERVICE_STEERING_UUID):
                        self.steering_service = service
                        print("[service uuid] ", self.steering_service.uuid)

                        if (self.steering_service != ""):
                            # print("SERVICE", SERVICE)
                            for characteristic in self.steering_service.characteristics:
                                
                                if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTICS_STEERING_UUID):
                                    self.steering_characteristics = characteristic
                                    # print("CHARACTERISTIC: ", CHARACTERISTIC_STEERING, characteristic.properties)
                                print("IF")

                        print(self.steering_ready)
                        self.steering_ready = 1 

                    if (service.uuid == self.SERVICE_TILT_UUID):
                        self.tilt_service = service
                        print("[service uuid] ", self.tilt_service.uuid)

                        if (self.tilt_service != ""):
                            for characteristic in self.tilt_service.characteristics:

                                print("characteristics UUID: ", characteristic.uuid)
                                if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTIC_TILT_UUID):
                                    self.tilt_characteristics = characteristic
                        self.tilt_ready = 1

                if (self.steering_ready == 1 and self.tilt_ready == 1):
                    print("all ready!")
                    self.init_ack = True

            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {self.DEVICE_UUID}: {e}")
                # Add additional error handling or logging as needed
                # raise

async def main():
    ble_async_init_task = asyncio.create_task(ble.async_init())
    await ble_async_init_task

    ble_handler_task = asyncio.create_task(ble.read_and_ride_rizer())
    print("ble main started")
    udp_handler_task = asyncio.create_task(udp.main())
    print("udp main start")
    await ble_handler_task
    await udp_handler_task

# Creating instances of handlers
udp = UDP_Handler()                
ble = BLE_Handler()

# Call async_init right after the instance is created
#asyncio.run(ble.async_init())


print("asyncio start")
asyncio.run(main())