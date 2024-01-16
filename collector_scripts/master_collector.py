import socket
import select
import json

class DataSender:
    def __init__(self):
        self.speed_value = 0
        self.steering_value = 0
        self.brake_value = 0
        self.bno_value = 0
        self.roll_value = 0
        self.udp_unity_send_ip = "127.0.0.2" # IP of the computer running Unity
        self.udp_unity_send_port = 1337
        
    def collect_speed(self, speed):
        self.speed_value = speed

    def collect_steering(self, steering):
        self.steering_value = steering
    
    def collect_brake(self, brake):
        self.brake_value = brake
    
    def collect_bno(self, bno):
        self.bno_value = bno
    
    def collect_roll(self, roll):
        self.roll_value = roll

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
            udp_socket.sendto(json_data.encode(), (self.udp_unity_send_ip, self.udp_unity_send_port))


# This class might be to be located in the headwind script
class DataReceiver:
    def __init__(self):
        self.ble_fan = 0
        self.udp_unity_receive_ip = "127.0.0.3"
        self.udp_unity_receive_port = 12345
        self.udp_socket = None
    
    '''
    def get_fan_speed(self):
        return self.ble_fan
    '''

    def start_udp_listener(self):
        # Create a UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Bind the socket to the specified IP and port
        self.udp_socket.bind((self.udp_unity_receive_ip, self.udp_unity_receive_port))
        
        print(f"UDP listener started on {self.udp_unity_receive_ip}:{self.udp_unity_receive_port}")
    
    def stop_udp_listener(self):
        if self.udp_socket:
            self.udp_socket.close()
            print("UDP listener stopped.")

    def listen_for_udp_data(self):
        while True:
            try:
                # Receive data from the socket
                data, addr = self.udp_socket.recvfrom(1024)
                
                # Assuming data is an integer sent in binary format
                self.ble_fan = int.from_bytes(data, byteorder='big')
                
                print(f"Received UDP data: {self.ble_fan}")
            except Exception as e:
                print(f"Error while receiving UDP data: {e}")



if __name__ == "__main__":
    data_sender = DataSender()
    data_receiver = DataReceiver()

    print("Master Collector script started...")
    # IP adresses to receive data from actuators and sensors
    UDP_IP = "127.0.0.1" # IP of the computer running this script
    UDP_ESP_IP = "192.168.9.185" # External IP of the computer running this script to receive data from ESP32

    # ports to receive data from actuators and sensors
    UDP_DIRETO = 1111
    UDP_RIZER = 2222
    UDP_ROLL = 6666
    UDP_BRAKE = 7777
    UDP_BNO = 8888


    udp_rizer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_rizer_socket.bind((UDP_IP, UDP_RIZER))

    udp_direto_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_direto_socket.bind((UDP_IP, UDP_DIRETO))

    udp_brake_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_brake_socket.bind((UDP_ESP_IP, UDP_BRAKE))

    udp_bno_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_bno_socket.bind((UDP_ESP_IP, UDP_BNO))

    udp_roll_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_roll_socket.bind((UDP_ESP_IP, UDP_ROLL))

    while True:
        data_sender.send_unity_data_udp(data_sender.speed_value, data_sender.steering_value, data_sender.brake_value, data_sender.bno_value, data_sender.roll_value)
        readable, _, _ = select.select([udp_rizer_socket, udp_direto_socket, udp_brake_socket, udp_bno_socket, udp_roll_socket], [], [])
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
                # print("Brake_value: ", brake_value)
                data_sender.collect_brake(brake_value)
            elif sock is udp_bno_socket:
                #print(f"Received data on port {UDP_BNO}: {data.decode()} from {addr}")
                bno_value = json.loads(data.decode())
                bno_value = bno_value["euler_r"]
                # print("BNO_Value: ", bno_value)
                data_sender.collect_bno(bno_value)


            elif sock is udp_roll_socket:
                #print(f"Received data on port {UDP_BNO}: {data.decode()} from {addr}")
                roll_value = json.loads(data.decode())
                print("Roll_Value: ", roll_value)
                roll_value = roll_value["sensor_value"]
                data_sender.collect_roll(roll_value)
            


            
