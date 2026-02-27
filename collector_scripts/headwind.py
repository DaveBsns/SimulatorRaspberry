import asyncio
from bleak import BleakScanner, BleakClient, exc
import socket
import json
import time

device_name = "HEADWIND BC55"

service_uuid = "a026ee0c-0a7d-4ab3-97fa-f1500f9feb8b"
characteristic_uuid = "a026e038-0a7d-4ab3-97fa-f1500f9feb8b"

UDP_IP = "127.0.0.3"
UDP_PORT = 2224

TIMEOUT_SECONDS = 3


async def connect_and_run(device):

    while True:
        try:
            async with BleakClient(device, timeout=60) as client:
                print("Connected to Headwind")

                # Start notify ONCE
                await client.start_notify(characteristic_uuid, lambda s, d: None)

                speed_value = 0
                last_packet_time = time.time()

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                    udp_socket.bind((UDP_IP, UDP_PORT))
                    udp_socket.setblocking(False)

                    print("Waiting for Unity UDP data...")

                    while True:

                        # --- RECEIVE UDP ---
                        try:
                            data, addr = udp_socket.recvfrom(64)
                            ble_fan_value = json.loads(data.decode())
                            speed_value = int(ble_fan_value["fanSpeed"])
                            last_packet_time = time.time()

                            print("Received fanSpeed:", speed_value)

                        except BlockingIOError:
                            pass

                        # --- TIMEOUT WATCHDOG ---
                        if time.time() - last_packet_time > TIMEOUT_SECONDS:
                            print("No Unity data detected. Resetting BLE...")
                            await client.write_gatt_char(characteristic_uuid, bytearray([0x04, 0x01]))
                            await client.disconnect()
                            break

                        # --- WRITE TO HEADWIND ---
                        try:
                            if speed_value > 0:
                                await client.write_gatt_char(characteristic_uuid, bytearray([0x04, 0x04]))
                                await asyncio.sleep(0.05)
                                await client.write_gatt_char(characteristic_uuid, bytearray([0x02, speed_value]))
                                print("Fan speed set to", speed_value)
                            else:
                                await client.write_gatt_char(characteristic_uuid, bytearray([0x04, 0x01]))
                                print("Fan turned OFF")

                        except Exception as e:
                            print("Write error:", e)

                        await asyncio.sleep(0.1)

        except exc.BleakError as e:
            print("BLE error:", e)
            await asyncio.sleep(2)


async def main():

    print("Scanning for Headwind...")

    device = None

    while device is None:
        devices = await BleakScanner.discover()
        for d in devices:
            if d.name == device_name:
                device = d
                break

        if device is None:
            print("Headwind not found. Retrying...")
            await asyncio.sleep(2)

    await connect_and_run(device)


if __name__ == "__main__":
    asyncio.run(main())