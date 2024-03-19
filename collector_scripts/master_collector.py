import asyncio
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
        self.udp_unity_send_ip = "127.0.0.2" # IP of the computer running Unity (just the localhost ip if the script is running on the same computer than the simulation)
        # self.udp_unity_send_ip = "10.30.77.221" # IP of the computer running Unity
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
        # self.udp_unity_receive_ip = "127.0.0.1"
        # self.udp_unity_receive_port = 12345
        self.udp_unity_receive_socket = None
        self.ble_fan_speed = 0
    
    
    def get_fan_speed(self):
        print("Self ble fan speed: ", self.ble_fan_speed)
        return self.ble_fan_speed
    
    def open_udp_socket(self):
        # Create a UDP socket
        udp_unity_receive_ip = "127.0.0.1"
        udp_unity_receive_port = 12345

        self.udp_unity_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_unity_receive_socket.bind((udp_unity_receive_ip, udp_unity_receive_port))

        print("Listening for UDP data...")

    def start_udp_listener(self):
        # Infinite loop to continuously receive data
        try:
            data, addr = self.udp_unity_receive_socket.recvfrom(1024)  # Buffer size is 1024 bytes  

            json_data = data.decode('utf-8')  # Decode bytes to string
            # value = json.loads(data.decode())
            unity_values = json.loads(json_data)
            ble_fan_value = unity_values["bleFan"]
            # print("ble fan from unity: ", ble_fan_value)
            self.ble_fan_speed = ble_fan_value
        except Exception as e:
            print(f"Error while receiving UDP data: {e}")

    def stop_udp_listener(self):
        if self.udp_unity_receive_socket:
            self.udp_unity_receive_socket.close()
            print("UDP listener stopped.")



if __name__ == "__main__":
    '''
    try:
        data_receiver.start_udp_listener()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Stopping the loop.")
    finally:
        pass
        # udp_unity_receive_socket.close()
    '''
    data_sender = DataSender()

    print("Master Collector script started...")
    # IP adresses to receive data from actuators and sensors
    UDP_IP = "127.0.0.1" # IP to receive data from elite_rizer.py as well as from direto_xr.py scripts via UDP
    # UDP_IP_UNITY_RECEIVE = "127.0.0.1" # Receives Data from unity such as the ble fan data
    UDP_ESP_IP = "10.30.77.40" # External IP of the computer running this script to receive data from ESP32 -> Bicycle Simulator Desktop PC
    # UDP_ESP_IP = "192.168.9.184" # Raspberry Pi 3
    # UDP_ESP_IP = "192.168.9.198" # Raspberry Pi 5

    # ports to receive data from actuators and sensors
    UDP_PORT_DIRETO = 1111
    UDP_PORT_RIZER = 2222
    UDP_PORT_ROLL = 6666
    UDP_PORT_BRAKE = 7777
    UDP_PORT_BNO = 8888
    # UDP_PORT_UNITY_RECEIVE = 12345 # Port to receive data from unity such as the ble fan data


    udp_rizer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_rizer_socket.bind((UDP_IP, UDP_PORT_RIZER))

    udp_direto_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_direto_socket.bind((UDP_IP, UDP_PORT_DIRETO))

    udp_brake_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_brake_socket.bind((UDP_ESP_IP, UDP_PORT_BRAKE))

    udp_bno_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_bno_socket.bind((UDP_ESP_IP, UDP_PORT_BNO))

    udp_roll_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_roll_socket.bind((UDP_ESP_IP, UDP_PORT_ROLL))

    # udp_unity_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udp_unity_receive_socket.bind((UDP_IP_UNITY_RECEIVE, UDP_PORT_UNITY_RECEIVE))

    
    
    while True:
        # print("udp_direto_socket: ", udp_direto_socket)
        data_sender.send_unity_data_udp(data_sender.speed_value, data_sender.steering_value, data_sender.brake_value, data_sender.bno_value, data_sender.roll_value)
        readable, _, _ = select.select([udp_rizer_socket, udp_direto_socket, udp_brake_socket, udp_bno_socket, udp_roll_socket], [], [])
        
        for sock in readable:
            data, addr = sock.recvfrom(1024)
            if sock is udp_rizer_socket:
                steering_value = data.decode()
                # print("steering: ", steering_value)
                data_sender.collect_steering(steering_value)
            elif sock is udp_direto_socket:
                speed_value = data.decode()
                # print("SPEED: ", speed_value)
                data_sender.collect_speed(speed_value)
            elif sock is udp_brake_socket:
                brake_value = json.loads(data.decode())
                brake_value = brake_value["sensor_value"]
                # print("Brake_value: ", brake_value)
                data_sender.collect_brake(brake_value)
            elif sock is udp_bno_socket:
                bno_value = json.loads(data.decode())
                bno_value = bno_value["euler_r"]
                # print("BNO_Value: ", bno_value)
                data_sender.collect_bno(bno_value)
            elif sock is udp_roll_socket:
                roll_value = json.loads(data.decode())
                # print("Roll_Value: ", roll_value)
                roll_value = roll_value["sensor_value"]
                data_sender.collect_roll(roll_value)
            '''
            elif sock is udp_unity_receive_socket:
                json_data = data.decode('utf-8')  # Decode bytes to string
                # value = json.loads(data.decode())
                unity_values = json.loads(json_data)
                ble_fan_value = unity_values["bleFan"]
                print("ble fan from unity: ", ble_fan_value)
            '''
