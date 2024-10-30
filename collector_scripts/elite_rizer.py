import asyncio
from bleak import BleakClient, exc
import socket
import time
import json

class Rizer:
    #BLE constant
    DEVICE_NAME = "RIZER"       
    DEVICE_UUID = "fc:12:65:28:cb:44"

    SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592"           # Rizer - read steering
    SERVICE_INCLINE_UUID = "347b0001-7635-408b-8918-8ff3949ce592"

    INCREASE_INCLINE_HEX = "060102"
    DECREASE_INCLINE_HEX = "060402"

    CHARACTERISTICS_STEERING_UUID = "347b0030-7635-408b-8918-8ff3949ce592"   # Rizer - read steering
    CHARACTERISTIC_INCLINE_UUID = "347b0020-7635-408b-8918-8ff3949ce592"     # write tilt

    #UDP constant
    UDP_IP_TO_MASTER_COLLECTOR = "127.0.0.1"        # Send the rizer data to the master_collector.py script via UDP over localhost
    UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.3"
    udp_port = 2222
    RECEIVE_FROM_MASTER_COLLECTOR_PORT = 2223

    _incline_value = 0
    incline_rate = 1
    incline_timer = 0



    def __init__(self) -> None:
        # UDP initialization
        self.received_steering_data = 0             # Initialize with None or any default value
        self.client_is_connected = False


        self.current_incline_on_rizer = int(0)
        self.udp_ip = "127.0.0.1" # Send the rizer data to the master_collector.py script via UDP over localhost
        # self.udp_ip = "10.30.77.221" # Ip of the Bicycle Simulator Desktop PC
        # self.udp_ip = "192.168.9.184" # IP of the Raspberry Pi
        self.udp_port = 2222
        print("init")

    async def main2(self):
        await self.connect_rizer()
        #asyncio.create_task(self.console_input_loop())

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.UDP_IP_FROM_MASTER_COLLECTOR, self.RECEIVE_FROM_MASTER_COLLECTOR_PORT))
            udp_socket.setblocking(False)

            while True:
                #await self.write_incline()
                await self.console_input_loop()
                time.sleep(0.1)  # prevent busy-waiting

    async def console_input_loop(self):
        """Loop to get incline input from console and send it to BLE device"""
        while True:
            try:
                incline_value = int(input("Enter incline (-20 to 40): "))
                if -20 <= incline_value <= 40:
                    self.set_incline_value(incline_value)
                    #print(f"Setting incline to {incline_value}")
                    
                    await self.write_incline2(incline_value > 0)
                    #print(f"new incline value: {self._incline_value}")
                else:
                    print("Please enter a value between -20 and 40.")
            except ValueError:
                print("Invalid input. Please enter an integer between -20 and 40.")

    async def read_and_print_position(self):
        """Continuously read and print the current incline position from the Rizer device."""
        while True:
            try:
                # Read the current incline value from the BLE characteristic
                position_data = await self.client.read_gatt_char(self.CHARACTERISTIC_INCLINE_UUID)
                # Convert the data from byte format to an integer or appropriate format
                current_position = int.from_bytes(position_data, byteorder='little', signed=True)
                print(f"Current Incline Position: {current_position}")
            except Exception as e:
                print(f"Error reading incline position: {e}")
            
            await asyncio.sleep(1)  # Adjust interval as needed (prints every 1 second here)

    async def main3(self):
        # first set current incline value to 0
        print("main")
        self.current_incline_on_rizer = 0

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.UDP_IP_FROM_MASTER_COLLECTOR, self.RECEIVE_FROM_MASTER_COLLECTOR_PORT))
            udp_socket.setblocking(False)
            # connect rizer
            await self.connect_rizer()

            for i in range(5):

                await self.write_incline2(up=True, updateValue= False)

            while True:

                
                # get data from UDP
                incline_value = 3000
                try:
                    udp_incline_data = 0
                    while True:
                        try:
                            udp_incline_data, addr = udp_socket.recvfrom(47)
                            sender_ip, sender_port = addr
                            print(f"Received message: {udp_incline_data.decode()} from {sender_ip}:{sender_port}")
                            incline_value = json.loads(udp_incline_data.decode())
                            incline_value = int(incline_value["rizerIncline"])                                                 # Extract the sender's IP and port from addr
                        except BlockingIOError:
                            break

                except BlockingIOError:
                    time.sleep(0.01)  # Small sleep to prevent busy-waiting



                if (incline_value < 3000):

                    # only if value has change write    
                    print("Got new Value from UDP: " + str(incline_value))
                    print("Current value incline: " + str(self.current_incline_on_rizer))

                    if (incline_value > self.current_incline_on_rizer and self.current_incline_on_rizer < 15):

                        print("UP 1")
                        await self.write_incline2(up= True)
                        #self.current_incline_on_rizer += 1

                    if (incline_value < self.current_incline_on_rizer and self.current_incline_on_rizer > -14):

                        print("DOWN 1")
                        await self.write_incline2(up= False)
                        #self.current_incline_on_rizer -= 1



    async def main(self):
        print("main")
        incline_value = 0

        # create UDP socket to receive data from master collector
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.UDP_IP_FROM_MASTER_COLLECTOR, self.RECEIVE_FROM_MASTER_COLLECTOR_PORT))
            udp_socket.setblocking(False)                                                                   # Set the socket to non-blocking mode | without this flag it waits until it gets data
            await self.connect_rizer()                                                                      #connect to the Rizer                                                                      
            while(True):
                # Receive data from the socket
                try:
                    udp_incline_data = 0
                    while True:
                        try:
                            udp_incline_data, addr = udp_socket.recvfrom(47)
                            sender_ip, sender_port = addr
                            print(f"Received message: {udp_incline_data.decode()} from {sender_ip}:{sender_port}")
                            incline_value = json.loads(udp_incline_data.decode())
                            incline_value = int(incline_value["rizerIncline"])                                                 # Extract the sender's IP and port from addr
                        except BlockingIOError:
                            break
                                                           

                except BlockingIOError:
                    time.sleep(0.01)  # Small sleep to prevent busy-waiting
                

                await self.write_incline()                                                          #write the new incline value to the Rizer

                self.set_incline_value(incline_value)
                if self.check_new_incline(incline_value):                                               #check if the incline value has changed
                    await self.write_incline()                                                          #write the new incline value to the Rizer

                await self.read_steering()                                                              #read steering over BLE ONLY WORKING with master_collector script!!!
                

#---------------------------UDP functions--------------------------------
    #send steering data over udp
    def send_steering_data_udp(self, steering_data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send steering_data
            udp_socket.sendto(str(steering_data).encode(), (self.UDP_IP_TO_MASTER_COLLECTOR, self.udp_port))

    #receive incline data over udp
    async def receive_incline_data_udp(self):
        udp_incline_data = 0
        # Set up the UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Bind the socket to the IP and port
            udp_socket.bind((self.UDP_IP_TO_MASTER_COLLECTOR, self.RECEIVE_FROM_MASTER_COLLECTOR_PORT))
            print("Hello: ", udp_incline_data)
            self.incline_value = udp_incline_data



#---------------------------BLE functions--------------------------------
    #function to initialize the BLE connection with the Rizer
    async def connect_rizer(self):
        print("start async init")
        while not self.client_is_connected:
            try:
                self.client = BleakClient(self.DEVICE_UUID, timeout=90)
                print("try to connect")
                await self.client.connect()
                self.client_is_connected = True
                print("Client connected to ", self.DEVICE_UUID)
                for service in self.client.services:
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

    #write incline to rizer over ble and store the value of his state
    async def write_incline(self):
        incline = self.get_incline_value()
        incline = int(incline)
        
        #print("current incline: ", int(self.current_incline_on_rizer), " Incline: ", int(incline) )
        #incline_different_temp = int(incline) - int(self.current_incline_on_rizer)         #absolute difference of old and new incline value
        #incline_different = abs(incline_different_temp)
        #print("incline_difference: ", incline_different)
        # print("Incline: ", incline, " current Incline: ", current_incline_on_rizer)

        if((int(incline) - int(self.current_incline_on_rizer)) > 0):
            #for x in range (incline_different):
                try:
                    await self.client.write_gatt_char(self.CHARACTERISTIC_INCLINE_UUID, bytes.fromhex(self.INCREASE_INCLINE_HEX), response=True)
                    self.current_incline_on_rizer += 1
                    #self.incline_received = 0
                    #print("incline written, x ", x)
                except Exception as e:
                    print("Error: ", e) 
        else:
            #for x in range (incline_different):
                try:
                    await self.client.write_gatt_char(self.CHARACTERISTIC_INCLINE_UUID, bytes.fromhex(self.DECREASE_INCLINE_HEX), response=True)
                    self.current_incline_on_rizer -= 1
                    #self.incline_received = 0
                    #print("incline written, x -", x)
                except Exception as e:
                    print("Error: ", e)

        #write incline to rizer over ble and store the value of his state
    async def write_incline2(self, up, updateValue = True):


        print(f"Current incline on Rizer: {self.current_incline_on_rizer}")
  

        if(up == True):
            #for x in range (incline_different):
                try:
                    await self.client.write_gatt_char(self.CHARACTERISTIC_INCLINE_UUID, bytes.fromhex(self.INCREASE_INCLINE_HEX), response=True)
                    if (updateValue): self.current_incline_on_rizer += 1
                    #self.incline_received = 0
                    #print("incline written, x ", x)
                except Exception as e:
                    print("Error: ", e) 
        else:
            #for x in range (incline_different):
                try:
                    await self.client.write_gatt_char(self.CHARACTERISTIC_INCLINE_UUID, bytes.fromhex(self.DECREASE_INCLINE_HEX), response=True)
                    if (updateValue): self.current_incline_on_rizer -= 1
                    #self.incline_received = 0
                    #print("incline written, x -", x)
                except Exception as e:
                    print("Error: ", e)

        print(f"New incline on Rizer: {self.current_incline_on_rizer}")

    #read steering from the Rizer
    async def read_steering(self):
        data = bytearray(8)
        sender = 0
        try:
            await self.client.start_notify(self.steering_characteristics, self.notify_steering_callback)
            # Access the notification data using data argument
            # print(f"Steering data: {sender}")
            # print(f"Steering data: {data}")
            await asyncio.sleep(0.1) # keeps the connection open for 10 seconds
            await self.client.stop_notify(self.steering_characteristics.uuid)                                  
        except Exception as e:
            print("Error: ", e) 



#---------------------------Utility functions--------------------------------
    def set_incline_value(self, incline):
        incline = min(int(incline), 40)
        incline = max(int(incline), -20)
        self._incline_value = incline

    def get_incline_value(self):
        return self._incline_value
    
    async def notify_steering_callback(self, sender, data):
            data = bytearray(data)
            steering = 0.0
            
            #we get this random values who stands for -1; 0 or 1
            if data[3] == 65:
                steering = 1.0
            elif data[3] == 193:
                steering = -1.0
            
            self.received_steering_data = steering
            print(self.received_steering_data)

            self.send_steering_data_udp(self.received_steering_data)

    #check if rizer alredy arrived position
    def check_new_incline(self, new_inline_udp):
        print(f"Old incline: {self.current_incline_on_rizer} and new {new_inline_udp}")
        if self.current_incline_on_rizer != new_inline_udp:
            print("incline value write BLE: ", self.get_incline_value())
            return True
        else:
            return False      

rizer = Rizer()
asyncio.run(rizer.main3())