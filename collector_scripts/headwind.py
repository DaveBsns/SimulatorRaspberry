import asyncio
from bleak import BleakScanner, BleakClient
from master_collector import DataReceiver

class BluetoothCallback:
    def __init__(self):
        self.received_data = 0  # Initialize with None or any default value

    async def notify_callback(self, sender, data):
        # Assuming data is received from the Bluetooth device
        print(data)


device_name = "HEADWIND BC55"  # Replace with the name of your desired BLE device
DEVICE = ""

service_uuid = "a026ee0c-0a7d-4ab3-97fa-f1500f9feb8b"
SERVICE = ""

characteristic_uuid = "a026e038-0a7d-4ab3-97fa-f1500f9feb8b" 
CHARACTERISTIC = ""

async def scan_and_connect():
    global device_name

    global service_uuid
    global SERVICE

    global characteristic_uuid
    global CHARACTERISTIC

    global value_to_write
    global old_value

    global is_first_entry
    global run_read_loop  

    stop_event = asyncio.Event()  

    # Scanning and printing for BLE devices
    def callback(device, advertising_data):
        global DEVICEID   
        print(device)
        if(device.name == device_name):
            DEVICEID = device
            stop_event.set()
            
    # Stops the scanning event    
    async with BleakScanner(callback) as scanner:
        await stop_event.wait()
    
    if(DEVICEID != ""):
        # Connecting to BLE Device
        async with BleakClient(DEVICEID, timeout=60) as client:
            print("Device ID ", DEVICEID)
            for service in client.services:
                 
                if (service.uuid == service_uuid):
                        SERVICE = service
     
                if (SERVICE != ""):
                    for characteristic in SERVICE.characteristics:
                        
                        if(characteristic.uuid == characteristic_uuid):
                            CHARACTERISTIC = characteristic

                            receiver = DataReceiver()
                            bluetooth_callback = BluetoothCallback()
                            while True:
                                try:
                                    await client.start_notify(CHARACTERISTIC, bluetooth_callback.notify_callback) # characteristic.uuid  
                                except Exception as e:
                                    print("Error: ", e)

                                # speed_input = input("Enter a value between 2-100 to set the fan speed. Enter 1 to turn on the fan. Enter 0 to turn off the fan (or 'x' to exit): ")
                                # speed_value = int(speed_input)
                                speed_value = 1
                                '''
                                if speed_input.lower() == 'x':
                                    await client.stop_notify(CHARACTERISTIC) # characteristic.uuid
                                    await asyncio.sleep(1)
                                    break
                                '''

                                ''' Test
                                receiver.start_udp_listener()
                                try:
                                    receiver.listen_for_udp_data()
                                except KeyboardInterrupt:
                                    receiver.stop_udp_listener()
                                '''

                                
                                try:
                                    if 2 <= speed_value <= 100:
                                        await client.write_gatt_char(CHARACTERISTIC, bytearray([0x02, speed_value]))
                                        print(f"Fan speed set to {speed_value}")
                                    elif speed_value == 1:
                                        await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x04])) # Turns fan on -> bytearray([0x04, 0x04]), Turns fan off -> bytearray([0x04, 0x01]), Adjust fan Speed -> bytearray([0x02, <Decimalvalue between 1 and 100>])
                                    elif speed_value == 0:
                                        await client.write_gatt_char(CHARACTERISTIC, bytearray([0x04, 0x01]))
                                    else:
                                        print("Speed value should be between 1 and 100.")
                                except ValueError:
                                    print("Invalid input. Please enter a number between 1 and 100.")

asyncio.run(scan_and_connect())