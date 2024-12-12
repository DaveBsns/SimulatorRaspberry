import asyncio
import json
import socket

# UDP Configuration
UDP_IP_TO_MASTER_COLLECTOR = "127.0.0.3"
SEND_TO_MASTER_COLLECTOR_PORT = 2225

UDP_IP_FROM_MASTER_COLLECTOR = "127.0.0.1"
RECEIVE_FROM_MASTER_COLLECTOR_PORT = 1111

async def send_resistance_data():
    """
    Send resistance data to the BLE device via UDP.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Sending resistance data to UDP...")

    while True:
        # Generate or fetch resistance data to send
        resistance_value = {
            "diretoResistance": 50  # Example value, replace with dynamic data as needed
        }

        resistance_message = json.dumps(resistance_value).encode()

        try:
            udp_socket.sendto(
                resistance_message, (UDP_IP_TO_MASTER_COLLECTOR, SEND_TO_MASTER_COLLECTOR_PORT)
            )
            print(f"Sent resistance data: {resistance_value}")
        except Exception as e:
            print(f"Error sending resistance data: {e}")

        await asyncio.sleep(1)  # Adjust interval as needed

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
    await asyncio.gather(
        send_resistance_data(),
        receive_speed_data()
    )

if __name__ == "__main__":
    asyncio.run(main())