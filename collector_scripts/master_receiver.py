from master_collector import DataReceiver
import json
import socket
import select


if __name__ == "__main__":
    print("Master Receiver started...")
    data_receiver = DataReceiver()

    # Create a UDP socket
    udp_unity_receive_ip = "127.0.0.1"
    udp_unity_receive_port = 12345

    udp_unity_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_unity_receive_socket.bind((udp_unity_receive_ip, udp_unity_receive_port))

    while True:
        print("Listening for UDP data...")
        readable, _, _ = select.select([udp_unity_receive_socket], [], [])
        for sock in readable:
            try:
                data, addr = sock.recvfrom(1024)
                if sock is udp_unity_receive_socket:
                    data = json.loads(data.decode())
                    unity_ble_fan_speed = data["bleFan"]
                    unity_ble_incline = data["bleIncline"]
                    unity_ble_resistance = data["bleResistance"]
                    print(unity_ble_incline, unity_ble_fan_speed)
                    data_receiver.send_udp_data_to_rizer(unity_ble_incline)
                    data_receiver.send_udp_data_to_headwind(unity_ble_fan_speed)
                    data_receiver.send_udp_data_to_direto(unity_ble_incline)

            except Exception as e:
                print(f"Error while receiving UDP data: {e}")




