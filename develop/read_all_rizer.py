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

    listen_data = {}


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

    async def on_steering_changed_to_json(self, sender, data):

        data = bytearray(data)
        print(f"")
        print(f"Sender {sender}: \n Steering changed: {[byte for byte in data]}")

    
    def save_to_json(self, filename="ble_device_data.json"):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"Data saved to {filename}")

    async def connect_rizer(self):
        print("Start async init")
        while not self.client_is_connected:
            try:
                self.client = BleakClient(self.DEVICE_UUID, timeout=90)
                print("Trying to connect")
                await self.client.connect()
                self.client_is_connected = True
                print(f"Client connected to {self.DEVICE_UUID}")
                
                # Initialize data structure
                self.data = {}
                
                for service in self.client.services:
                    service_uuid = str(service.uuid)
                    self.data[service_uuid] = []
                    
                    for characteristic in service.characteristics:
                        char_uuid = str(characteristic.uuid)
                        char_data = {
                            "uuid": char_uuid,
                            "properties": characteristic.properties,
                            "data": []
                        }
                        self.data[service_uuid].append(char_data)
                        

                        print(f"=== Trying to read Data for {char_uuid}:")
                        
                        try:
                            value = await self.client.read_gatt_char(characteristic.uuid)
                            data = bytearray(value)
                            print(f"=== Data: {[byte for byte in data]}")
                            
                            # Store the data
                            char_data["data"].append([byte for byte in data])
                        except exc.BleakError as e:
                            print(f"=== Failed to read Data!")
                            char_data["error"] = str(e)
                        
                        print("\n")

            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {self.DEVICE_UUID}: {e}")

        return self.data




rizer = TestRizer()

async def main():

    config = "middle"
    await rizer.connect_rizer()

    rizer.save_to_json(filename= config +"_ble_device_data.json")



    '''
    for charc in rizer.listCharacteristic:

        await rizer.start_notification(characteristic = charc)

    # Keep the connection alive for a while
    await asyncio.sleep(60)

    await rizer.stop_notification()'''

asyncio.run(main())
