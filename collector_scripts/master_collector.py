import socket
import select
import json

class DataCollector:
    def __init__(self):
        self.speed_value = 0
        self.steering_value = 0
        self.brake_value = 0
        self.bno_value = 0
    
    def collect_speed(self, speed):
        self.speed_value = speed

    def collect_steering(self, steering):
        self.steering_value = steering
    
    def collect_brake(self, brake):
        self.brake_value = brake
    
    def collect_bno(self, bno):
        self.bno_value = bno

class DataSender:
    # data_collector = DataCollection()
    def __init__(self):
        self.speed_value = 0
        self.steering_value = 0
        self.brake_value = 0
        self.bno_value = 0
        self.udp_unity_ip = "127.0.0.2"
        self.udp_unity_port = 1337
        

    def collect_speed(self, speed):
        self.speed_value = speed

    def collect_steering(self, steering):
        self.steering_value = steering
    
    def collect_brake(self, brake):
        self.brake_value = brake
    
    def collect_bno(self, bno):
        self.bno_value = bno

    def send_unity_data_udp(self, speed_data, steering_data, brake_data, bno_data, roll_data):
        

        # Create a dictionary with the required parameters
        data = {
            "diretoSpeed": float(speed_data),
            "rizerSteering": float(steering_data),
            "espBno": float(bno_data),
            "espBrake": float(brake_data),
            "espRoll": float(roll_data)
        }
        print(data)
        # Convert dictionary to JSON string
        json_data = json.dumps(data)

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send JSON data
            udp_socket.sendto(json_data.encode(), (self.udp_unity_ip, self.udp_unity_port))



if __name__ == "__main__":
    data_sender = DataSender()

    print("Master Collector script started...")
    # IP adresses to receive data from actuators and sensors
    UDP_IP = "127.0.0.1"
    UDP_ESP_IP = "192.168.9.185"  

    # ports to receive data from actuators and sensors
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
        data_sender.send_unity_data_udp(data_sender.speed_value, data_sender.steering_value, data_sender.brake_value, data_sender.bno_value, 0)
        readable, _, _ = select.select([udp_rizer_socket, udp_direto_socket, udp_brake_socket, udp_bno_socket], [], [])
        for sock in readable:
            data, addr = sock.recvfrom(1024)
            if sock is udp_rizer_socket:
                #print(f"Received data on port {UDP_RIZER}: {data.decode()} from {addr}")
                steering_value = data.decode()
                data_sender.collect_steering(steering_value)
            elif sock is udp_direto_socket:
                #print(f"Received data on port {UDP_DIRETO}: {data.decode()} from {addr}")
                speed_value = data.decode()
                data_sender.collect_speed(speed_value)
            elif sock is udp_brake_socket:
                #print(f"Received data on port {UDP_BRAKE}: {data.decode()} from {addr}")
                brake_value = json.loads(data.decode())
                brake_value = brake_value["sensor_value"]
                print("Brake_value: ", brake_value)
                data_sender.collect_brake(brake_value)
            elif sock is udp_bno_socket:
                #print(f"Received data on port {UDP_BNO}: {data.decode()} from {addr}")
                bno_value = json.loads(data.decode())
                bno_value = bno_value["euler_r"]
                print("BNO_Value: ", bno_value)
                data_sender.collect_bno(bno_value)
            


            
