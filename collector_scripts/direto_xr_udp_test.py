import asyncio
import json
import socket
import aioconsole

# UDP Configuration
UDP_IP_TO_MASTER_COLLECTOR = "127.0.0.3"
SEND_TO_MASTER_COLLECTOR_PORT = 2225

UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.1"
RECEIVE_FROM_MASTER_COLLECTOR_PORT = 1111
resistance_value = 0

async def prompt_resistance():
    global resistance_value
    while True:
        new_value = await aioconsole.ainput("Enter resistance value (0-100): ")
        if new_value:
            resistance_value = int(new_value)

async def send_resistance_data():
    """
    Send resistance data to the BLE device via UDP.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global resistance_value
    print("Sending resistance data to UDP...")

    while True:
        print(f"Resistance value: {resistance_value}")
        resistance_message = json.dumps({"diretoResistance": resistance_value}).encode()
        try:
            udp_socket.sendto(
                resistance_message, (UDP_IP_TO_MASTER_COLLECTOR, SEND_TO_MASTER_COLLECTOR_PORT)
            )
            print(f"Sent resistance data: {resistance_value}")
        except Exception as e:
            print(f"Error sending resistance data: {e}")

        await asyncio.sleep(0.01)  # Adjust interval as needed

async def receive_speed_data():
    """
    Receive speed data from the BLE device via UDP.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP_FROM_MASTER_COLLECTOR, RECEIVE_FROM_MASTER_COLLECTOR_PORT))
    print("Listening for speed data on UDP...")

    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            speed_value = data.decode()
            print(f"Received speed data: {speed_value} from {addr}")
        except Exception as e:
            print(f"Error receiving speed data: {e}")

        await asyncio.sleep(0.1)  # Adjust interval as needed

async def main():
    global resistance_value
    resistance_value = 0
    await asyncio.gather(
        prompt_resistance(),
        send_resistance_data(),
        receive_speed_data(),
    )

if __name__ == "__main__":
    asyncio.run(main())