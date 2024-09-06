import asyncio
from bleak import BleakClient, exc, BleakScanner
import socket
import time
import json

class TestRizer:

    #BLE constant
    DEVICE_NAME = "RIZER"       
    DEVICE_UUID = "fc:12:65:28:cb:44"

    SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592" 
    CHARACTERISTICS_STEERING_UUID = "347b0030-7635-408b-8918-8ff3949ce592"

    client_is_connected = False
    listCharacteristic = []


#---------------------------BLE functions--------------------------------
    #function to initialize the BLE connection with the Rizer
    async def start_notification(self, characteristic):
        print("characteristic: ", characteristic)
        if self.client_is_connected:
            try:
                #for characteristic in self.listCharacteristic:
                await self.client.start_notify(
                characteristic,
                self.on_steering_changed
                )
                print("Started notification for steering characteristic")
            except Exception as e:
                print(f"Failed to start notification: {e}")
        else:
            print("Not connected to the device")

    async def stop_notification(self):
        if self.client_is_connected:
            try:
                await self.client.stop_notify()
                print("Stopped notification for steering characteristic")
            except Exception as e:
                print(f"Failed to stop notification: {e}")

    async def on_steering_changed(self, sender, data):
        data = bytearray(data)
        print(f"")
        print(f"Sender {sender}: \n Steering changed: {[byte for byte in data]}")


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
                    #if (service.uuid == self.SERVICE_STEERING_UUID):
                    #self.steering_service = service
                    #print("[service uuid] ", self.steering_service.uuid)
                    print(f"\n[Service UUID: {service}]\n")

                    #if (self.steering_service != ""):
                        #print("SERVICE", self.steering_service)
                    #for characteristic in self.steering_service.characteristics:
                    for characteristic in service.characteristics:
                        print("Characteristic: ", characteristic)
                        print("Properties: ", characteristic.properties)
                        print("\n")

                    
                        '''try:
                            value = await self.client.read_gatt_char(characteristic.uuid)
                            data = bytearray(value)
                            print(f"Read value from {characteristic.uuid}: {[byte for byte in data]}")
                        except exc.BleakError as e:
                            print(f"Failed to read from {characteristic.uuid}: {e}")
                        
                        if("notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTICS_STEERING_UUID):
                            self.listCharacteristic.append(characteristic)
                            #self.steering_characteristics = characteristic
                            print("CHARACTERISTIC: ", self.CHARACTERISTICS_STEERING_UUID, characteristic.properties)
                        '''

            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {self.DEVICE_UUID}: {e}")
                # Add additional error handling or logging as needed
                # raise



rizer = TestRizer()

async def main():
    await rizer.connect_rizer()
    # this way we can listen to as many as we want!
    # To Do: 
    # Iterate trough all services and find all characterisitcs 
    # with notify 
    # Then listen to all and create a plot for each in real time 
    # Then we can find all values that change if steering changes 

    # for those wich do not have the noftiy type we coulde habve to read the char
    # value = await characteristic.read()
    # self.steering_position = bytearray(value)
    # print(f"Current steering position: {[byte for byte in self.steering_position]}")


    #for charc in rizer.listCharacteristic:

        #await rizer.start_notification(characteristic = charc)

    # Keep the connection alive for a while
    #await asyncio.sleep(60)

    #await rizer.stop_notification()

asyncio.run(main())

