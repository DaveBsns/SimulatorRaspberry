import socket

def start_udp_server(host, port):
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # Bind the socket to a specific address and port
        server_socket.bind((host, port))
        print(f"UDP server listening on {host}:{port}")

        while True:
            # Receive data from the client
            data, client_address = server_socket.recvfrom(1024)
            print(f"Received data from {client_address}: {data.decode('utf-8')}")

if __name__ == "__main__":
    # Set the host and port you want to listen on
    host = "127.0.0.1"  # Use "0.0.0.0" to listen on all available interfaces
    port = 12345

    start_udp_server(host, port)
