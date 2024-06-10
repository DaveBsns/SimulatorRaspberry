import asyncio
from bleak import BleakClient, exc
import socket
import time
from master_collector import DataReceiverSingleton

#global variables
global incline_received                         #received tilt data form UDP. Ready to send over BLE
global steering_received                        #received steering data from RIZER. Ready to send over UDP
global incline_value
current_tilt_value_on_razer = None              #received tilt data form UDP. Ready to send over BLE
client = None
asyncio_sleep = 3
steering_ready_to_send = 0                     


class UDP_Handler:

    def __init__(self):
        global incline_value
        global incline_received

        incline_value = 0
        incline_received = 0
        self.received_steering_data = 0  # Initialize with None or any default value
        self.udp_ip = "127.0.0.1" # Send the rizer data to the master_collector.py script via UDP over localhost
        self.udp_port = 2222
        print("udp handler started")
            

    async def main(self):
        global incline_value
        global steering_received
        global asyncio_sleep
        self.steering_data = None
        steering_received = None
        receiver = DataReceiverSingleton.get_instance()
        print("rizer id: ", id(receiver))
        print("where id??")
        while(True):
            await asyncio.sleep(asyncio_sleep)
            print("udp main")
            if (steering_received == 1):                                  #when steering value has chanched, send it to unity
                print("send steering data")
                await self.send_steering_data_udp(self.steering_data)
            try:
                #self.receiver._receiver.start_udp_listener()
                print("datareceiver get incline", receiver._instance.get_incline())
                print("datareceiver get fan", receiver._instance.get_fan_speed())

                #self.receiver._receiver.stop_udp_listener()
                incline_value = receiver._instance.get_incline()     #read tilt from unity
                #print("fan speed (b c)", self.receiver.get_fan_speed())
                print("incline from UDP (b c): ", incline_value)
                self.check_new_incline(incline_value)                     #check if tilt value has changed or is still the same

            except Exception as e:
                print("Error: ", e)

            print("udp loop finish")

 #   async def udp_handler_listen(self):
 #       print("open udp socket")
 #       self.receiver.open_udp_socket()
        

    
    def set_incline_received(self, received):
        self.incline_received = received
    
    def get_incline_received(self):
        return self.incline_received

    #send steering data over udp
    def send_steering_data_udp(self, steering_data):
        # Create a UDP socket
        #print("send steering data: ", steering_data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send speed_data
            udp_socket.sendto(str(steering_data).encode(), (self.udp_ip, self.udp_port))

    def listening_udp(self):
        udp_incline_data = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.listen(str(udp_incline_data).encode(), (self.udp_ip, self.udp_port))
            print("Hello: ", udp_incline_data)
    
    # check if the value of the tilt in unity is the same as on the rizer (currently not possible to check the value. just to store the changes)
    def check_new_incline(self, udp_incline_value):
        global incline_value
        print("RIZER incline: ", udp_incline_value)
        if incline_value != udp_incline_value:
            incline_value = udp_incline_value
            self.incline_received = 1

class BLE_Handler:
    #BLE constant
    DEVICE_NAME = "RIZER"       
    DEVICE_UUID = "fc:12:65:28:cb:44"

    SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592"           # Rizer - read steering
    SERVICE_INCLINE_UUID = "347b0001-7635-408b-8918-8ff3949ce592"

    INCREASE_INCLINE_HEX = "060102"
    DECREASE_TILT_HEX = "060402"

    CHARACTERISTICS_STEERING_UUID = "347b0030-7635-408b-8918-8ff3949ce592"   # Rizer - read steering
    CHARACTERISTIC_INCLINE_UUID = "347b0020-7635-408b-8918-8ff3949ce592"     # write tilt

    global steering_characteristics
    global tilt_characteristics

    global steering_service
    global tilt_service

    global current_tilt_value_on_razer                          # current position of RIZER (save ervery change for verification)

    def __init__(self):
        global steering_characteristics
        global tilt_characteristics

        global steering_service
        global tilt_service

        #global steering_ready                   #connection to steering BLE service ready
        #global tilt_ready                       #connection to tilt BLE service ready

        #global client_is_connected
        #global client_is_connected
        
        # Connecting to BLE Device
        print("Connecting to BLE Device")
        self.client_is_connected = False
        self.steering_ready = 0
        self.incline_ready = 0
        self.tilt_received = 0
        self.steering_characteristics = None
        self.incline_characteristics = 0
        self.init_ack = False
    
    #main function for BLE Handler
    async def read_and_ride_rizer(self):
        global incline_received
        global client
        print("read and write")
        while(True):
            await asyncio.sleep(asyncio_sleep)
            print("udp handler sleep")
            if (self.init_ack == True):
                await self.read_steering()
                print("read steering rizer")
                if (incline_received == 1):
                    await self.write_incline(client)
            else:
                print("wait init ack")


    async def read_steering(self):
        data = bytearray(8)
        sender = 0
        await asyncio.sleep(asyncio_sleep)
        try:
            await client.start_notify(self.steering_characteristics, self.notify_steering_callback)
            # Access the notification data using data argument
            #print(f"Steering data: {sender}")
            #print(f"Steering data: {data}")
            await asyncio.sleep(0.5) # keeps the connection open for 10 seconds
            await client.stop_notify(self.steering_characteristics.uuid)                                  
        except Exception as e:
            print("Error: ", e)                    

    async def write_incline(self): #TODO + - inclne 
        global client
        try:
            await client.write_gatt_char(self.CHARACTERISTIC_INCLINE_UUID, bytes.fromhex(self.INCREASE_INCLINE_HEX), response=True)
            current_tilt_value_on_razer += 0.5
            self.incline_received = 0
            print("tilt writed")
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
        print("readed steering: ", self.received_steering_data)
        udp.send_steering_data_udp(self.received_steering_data)

    async def async_init(self):
        global client
        print("start async init")
        while not self.client_is_connected:
            try:
                client = BleakClient(self.DEVICE_UUID, timeout=90)
                print("try to connect")
                await client.connect()
                self.client_is_connected = True
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

                        #print("steering ready", self.steering_ready)
                        self.steering_ready = 1 

                    if (service.uuid == self.SERVICE_INCLINE_UUID):
                        self.incline_service = service
                        print("[service uuid] ", self.incline_service.uuid)

                        if (self.incline_service != ""):
                            for characteristic in self.incline_service.characteristics:

                                print("characteristics UUID: ", characteristic.uuid)
                                if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTIC_INCLINE_UUID):
                                    self.incline_characteristics = characteristic
                        self.incline_ready = 1

                if (self.steering_ready == 1 and self.incline_ready == 1):
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
#    udp_listener_task = asyncio.create_task(udp.udp_handler_listen())
    await ble_handler_task
    await udp_handler_task
 #   print("start udp listener")
 #   await udp_listener_task

# Creating instances of handlers
udp = UDP_Handler()                
ble = BLE_Handler()

# Call async_init right after the instance is created
#asyncio.run(ble.async_init())

asyncio.run(main())