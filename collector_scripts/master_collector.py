import socket
import select
import json

UDP_IP = "127.0.0.1"
UDP_ESP_IP = "192.168.9.185"  

UDP_DIRETO = 1111
UDP_RIZER = 2222
UDP_BRAKE = 7777
UDP_BNO = 8888

# Create the second UDP socket
udp_rizer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_rizer_socket.bind((UDP_IP, UDP_RIZER))

# Create the first UDP socket
udp_direto_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_direto_socket.bind((UDP_IP, UDP_DIRETO))

# Create the first UDP socket
udp_brake_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_brake_socket.bind((UDP_ESP_IP, UDP_BRAKE))

# Create the first UDP socket
udp_bno_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_bno_socket.bind((UDP_ESP_IP, UDP_BNO))


    
while True:
    readable, _, _ = select.select([udp_rizer_socket, udp_direto_socket, udp_brake_socket, udp_bno_socket], [], [])
    for sock in readable:
        data, addr = sock.recvfrom(1024)
        if sock is udp_rizer_socket:
            print(f"Received data on port {UDP_RIZER}: {data.decode()} from {addr}")
        elif sock is udp_direto_socket:
            print(f"Received data on port {UDP_DIRETO}: {data.decode()} from {addr}")
        elif sock is udp_brake_socket:
            print(f"Received data on port {UDP_BRAKE}: {data.decode()} from {addr}")
        elif sock is udp_bno_socket:
            print(f"Received data on port {UDP_BNO}: {data.decode()} from {addr}")