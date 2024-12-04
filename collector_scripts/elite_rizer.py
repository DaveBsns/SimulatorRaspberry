import asyncio
from bleak import BleakClient, exc
import socket
import time
import json


class Rizer:
    """Class to control the Rizer BLE device for simulating bike inclines in a VR environment."""

    # BLE constants
    DEVICE_NAME = "RIZER"
    DEVICE_UUID = "fc:12:65:28:cb:44"

    SERVICE_STEERING_UUID = "347b0001-7635-408b-8918-8ff3949ce592"  # UUID for steering service
    SERVICE_INCLINE_UUID = "347b0001-7635-408b-8918-8ff3949ce592"  # UUID for incline service

    INCREASE_INCLINE_HEX = "060102"  # Command to increase incline
    DECREASE_INCLINE_HEX = "060402"  # Command to decrease incline

    CHARACTERISTICS_STEERING_UUID = "347b0030-7635-408b-8918-8ff3949ce592"  # Characteristic UUID for steering
    CHARACTERISTIC_INCLINE_UUID = "347b0020-7635-408b-8918-8ff3949ce592"    # Characteristic UUID for incline control

    # UDP constants
    UDP_IP_TO_MASTER_COLLECTOR = "127.0.0.1"  # IP address to send data to master_collector.py
    UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.3"  # IP address to receive data from master_collector.py
    UDP_PORT = 2222  # UDP port for sending data
    RECEIVE_FROM_MASTER_COLLECTOR_PORT = 2223  # UDP port for receiving data

    # Initial incline values and rate
    _incline_value = 0
    incline_rate = 1
    incline_timer = 0

    def __init__(self) -> None:
        # Initialize UDP communication
        self.received_steering_data = 0  # Initialize steering data
        self.client_is_connected = False  # BLE client connection status

        self.current_incline_on_rizer = 0  # Current incline position on the Rizer device

        self.udp_ip = "127.0.0.1"  # IP address for UDP communication
        # Alternative IP addresses can be set if needed
        # self.udp_ip = "10.30.77.221"  # IP of the Bicycle Simulator Desktop PC
        # self.udp_ip = "192.168.9.184"  # IP of the Raspberry Pi

        self.udp_port = 2222  # UDP port for communication
        print("Initializing Rizer control module")

    async def read_and_print_position(self):
        """Continuously read and print the current incline position from the Rizer device."""
        while True:
            try:
                # Read the current incline value from the BLE characteristic
                position_data = await self.client.read_gatt_char(self.CHARACTERISTIC_INCLINE_UUID)
                # Convert the data from byte format to an integer
                current_position = int.from_bytes(position_data, byteorder='little', signed=True)
                print(f"Current Incline Position: {current_position}")
            except Exception as e:
                print(f"Error reading incline position: {e}")
            await asyncio.sleep(1)  # Adjust interval as needed (currently prints every 1 second)

    async def main(self):
        """Main function to control the Rizer device based on UDP input."""
        # Initialize the current incline value
        self.current_incline_on_rizer = 0

        # Create a UDP socket to receive data from the master_collector script
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Bind the socket to receive data from the specified IP and port
            udp_socket.bind((self.UDP_IP_FROM_MASTER_COLLECTOR, self.RECEIVE_FROM_MASTER_COLLECTOR_PORT))
            udp_socket.setblocking(False)  # Set socket to non-blocking mode

            # Connect to the Rizer device via BLE
            await self.connect_rizer()

            # Send initial incline commands to the Rizer device
            for i in range(5):
                await self.write_incline(up=True, updateValue=False)

            while True:
                # Default incline value indicating no valid data received
                incline_value = 3000
                try:
                    # Receive data from the UDP socket
                    udp_incline_data = None
                    while True:
                        try:
                            # Receive data from the socket
                            udp_incline_data, addr = udp_socket.recvfrom(47)
                            sender_ip, sender_port = addr
                            print(f"Received message: {udp_incline_data.decode()} from {sender_ip}:{sender_port}")
                            # Parse the received data as JSON and extract the incline value
                            incline_data = json.loads(udp_incline_data.decode())
                            incline_value = int(incline_data["rizerIncline"])
                        except BlockingIOError:
                            # No more data to read from socket
                            break
                except BlockingIOError:
                    # No data received; sleep briefly to prevent busy-waiting
                    time.sleep(0.01)

                if incline_value < 3000:
                    # Only proceed if a valid incline value was received
                    print("Got new Value from UDP: " + str(incline_value))
                    print("Current value incline: " + str(self.current_incline_on_rizer))

                    if incline_value > self.current_incline_on_rizer and self.current_incline_on_rizer < 15:
                        # If the desired incline is higher than the current, and within bounds, increase incline
                        print("Increasing incline by 1")
                        await self.write_incline(up=True)

                    if incline_value < self.current_incline_on_rizer and self.current_incline_on_rizer > -14:
                        # If the desired incline is lower than the current, and within bounds, decrease incline
                        print("Decreasing incline by 1")
                        await self.write_incline(up=False)


    async def connect_rizer(self):
        """Initialize the BLE connection with the Rizer device."""
        print("Starting BLE connection initialization")
        while not self.client_is_connected:
            try:
                # Create a BLE client to connect to the Rizer device
                self.client = BleakClient(self.DEVICE_UUID, timeout=90)
                print("Attempting to connect to Rizer device")
                await self.client.connect()
                self.client_is_connected = True
                print(f"Client connected to {self.DEVICE_UUID}")

                # Discover services and characteristics on the Rizer device
                for service in self.client.services:
                    if service.uuid == self.SERVICE_STEERING_UUID:
                        self.steering_service = service
                        print(f"Found steering service with UUID: {self.steering_service.uuid}")

                        if self.steering_service != "":
                            for characteristic in self.steering_service.characteristics:
                                if "notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTICS_STEERING_UUID:
                                    self.steering_characteristics = characteristic

                        self.steering_ready = 1  # Indicate that steering service is ready

                    if service.uuid == self.SERVICE_INCLINE_UUID:
                        self.incline_service = service
                        print(f"Found incline service with UUID: {self.incline_service.uuid}")

                        if self.incline_service != "":
                            for characteristic in self.incline_service.characteristics:
                                print(f"Found characteristic UUID: {characteristic.uuid}")
                                if "notify" in characteristic.properties and characteristic.uuid == self.CHARACTERISTIC_INCLINE_UUID:
                                    self.incline_characteristics = characteristic

                        self.incline_ready = 1  # Indicate that incline service is ready

                if self.steering_ready == 1 and self.incline_ready == 1:
                    print("All services are ready!")
                    self.init_ack = True  # Acknowledge that initialization is complete

            except exc.BleakError as e:
                print(f"Failed to connect/discover services of {self.DEVICE_UUID}: {e}")
                # Additional error handling or retry logic can be added here

    async def write_incline(self, up, updateValue=True):
        """Send command to adjust the incline of the Rizer device.

        Args:
            up (bool): True to increase incline, False to decrease incline.
            updateValue (bool): Whether to update the current incline value after the command.
        """
        print(f"Current incline on Rizer: {self.current_incline_on_rizer}")

        try:
            if up:
                # Send command to increase incline
                await self.client.write_gatt_char(
                    self.CHARACTERISTIC_INCLINE_UUID,
                    bytes.fromhex(self.INCREASE_INCLINE_HEX),
                    response=True
                )
                if updateValue:
                    self.current_incline_on_rizer += 1
            else:
                # Send command to decrease incline
                await self.client.write_gatt_char(
                    self.CHARACTERISTIC_INCLINE_UUID,
                    bytes.fromhex(self.DECREASE_INCLINE_HEX),
                    response=True
                )
                if updateValue:
                    self.current_incline_on_rizer -= 1
        except Exception as e:
            print(f"Error sending incline command: {e}")

        print(f"New incline on Rizer: {self.current_incline_on_rizer}")


if __name__ == "__main__":
    # Create an instance of Rizer and run the main control loop
    rizer = Rizer()
    asyncio.run(rizer.main())
