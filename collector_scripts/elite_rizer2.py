import asyncio
from bleak import BleakClient, exc
import socket
import time
from master_collector import DataReceiver

#Global BLE variables
steering_service = ""
tilt_service = ""

steering_characteristics = ""
tilt_characteristics = ""

stering_ready = 0
tilt_ready = 0

stored_tilt_value = 0


async def scan_and_connect_rizer():

    #BLE constant
    DEVICE_NAME = "RIZER"       
    DEVICE_UUID = "fc:12:65:28:cb:44"

    SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592" # Rizer - read steering
    SERVICE_TILT_UUID = "347b0001-7635-408b-8918-8ff3949ce592"

    INCREASE_TILT_HEX = "060102"
    DECREASE_TILT_HEX = "060402"

    CHARACTERISTICS_STEEING_UUID = "347b0030-7635-408b-8918-8ff3949ce592" # Rizer - read steering
    CHARACTERISTIC_TILT_UUID = "347b0020-7635-408b-8918-8ff3949ce592" # write tilt

    
    # Connecting to BLE Device
    client_is_connected = False
    while(client_is_connected == False):
        try:
            async with BleakClient(DEVICE_UUID, timeout=90) as client:
                client_is_connected = True
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