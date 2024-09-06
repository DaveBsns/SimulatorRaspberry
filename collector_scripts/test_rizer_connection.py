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
    client_is_connected = False

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
                            print("SERVICE", self.steering_service)
                            for characteristic in self.steering_service.characteristics:
                                print(characteristic)
                                if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTICS_STEERING_UUID):
                                    self.steering_characteristics = characteristic
                                #     # print("CHARACTERISTIC: ", self.CHARACTERISTICS_STEERING_UUID, characteristic.properties)


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
                    self.current_incline_on_rizer += -1
                    #self.incline_received = 0
                    #print("incline written, x -", x)
                except Exception as e:
                    print("Error: ", e)

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
            
            self.rtself.received_steering_data

            self.send_steering_data_udp(self.received_steering_data)

    #check if rizer alredy arrived position
    def check_new_incline(self, new_inline_udp):
        if self.current_incline_on_rizer != new_inline_udp:
            print("incline value write BLE: ", self.get_incline_value())
            return True
        else:
            return False      

rizer = Rizer()
asyncio.run(rizer.connect_rizer())