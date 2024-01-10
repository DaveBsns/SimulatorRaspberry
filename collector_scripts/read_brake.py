import socket
import json

UDP_IP = "192.168.9.185"  # Listen to all incoming UDP packets
UDP_PORT = 7777  # Same port as used in the Arduino script

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

while True:
    data, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
    received_data = data.decode()

    try:
        # Attempt to parse the received JSON data
        json_data = json.loads(received_data)
        print("Received JSON data:")
        print(json.dumps(json_data, indent=4))  # Print the JSON data nicely formatted
    except json.JSONDecodeError as e:
        print("Received data is not in JSON format.")
        print(f"Received data: {received_data}")

    print(f"Received data from {addr}")
