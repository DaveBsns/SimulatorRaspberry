import asyncio
import socket
import select
import json
import time

class DataSender:
    def __init__(self):
        self.speed_value = 0
        self.steering_value = 0
        self.steering_angle = 0
        self.brake_value = 0
        self.bno_value = 0
        self.roll_value = 0
        self.udp_unity_send_ip = "127.0.0.2" # IP of the computer running Unity (just the localhost ip if the script is running on the same computer than the simulation)
        self.udp_unity_send_port = 1337
        
    def collect_speed(self, speed):
        self.speed_value = speed

    def collect_steering(self, steering):
        self.steering_value = steering
    
    def collect_brake(self, brake):
        self.brake_value = brake
    
    def collect_bno(self, bno):
        self.bno_value = bno

    def collect_steering_angle(self, steering_angle):
        self.steering_angle = steering_angle

    
    def collect_roll(self, roll):
        self.roll_value = roll

    def send_unity_data_udp(self, speed_data, steering_data, brake_data, bno_data, roll_data, steering_angle):
        
        # Create a dictionary with the required parameters
        data = {
            "diretoSpeed": float(speed_data),
            "rizerSteering": float(steering_data),
            "espBno": float(bno_data),
            "espBrake": float(brake_data),
            "espRoll": float(roll_data),
            "steeringAngle": float(steering_angle)
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
        self.ble_fan_speed = 0
        self.ble_incline = 40
        self.ble_resistance = 0
        self.ble_resistance = 0
        self.send_to_actuator_ip = "127.0.0.3"
        self.send_to_rizer_port = 2223
        self.send_to_headwind_port = 2224
        self.send_to_direto_port = 2225
    
    def set_ble_fan_speed(self, fan_speed):
        self.ble_fan_speed = fan_speed

    def set_ble_incline(self, incline_data):
        self.ble_incline = incline_data
        print("Self incline data: ", self.ble_incline)

    def get_fan_speed(self):
        #global ble_fan_speed
        print("Self ble fan speed: ", self.ble_fan_speed)
        return self.ble_fan_speed
    
    def get_incline(self):
        print("Self ble incline: ", self.ble_incline)
        return self.ble_incline
    
    def get_resistance(self):
        #global ble_resistance
        print("Self ble resistance: ", self.ble_resistance)
        return self.ble_resistance
    
    def send_udp_data_to_rizer(self, incline_data):
        # Create a dictionary with the required parameters
        data = {
            "rizerIncline": float(incline_data),
        }
        print(data)
        # Convert dictionary to JSON string
        json_data = json.dumps(data)

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send JSON data
            udp_socket.sendto(json_data.encode(), (self.send_to_actuator_ip, self.send_to_rizer_port))


    def send_udp_data_to_headwind(self, fan_speed):
        # Create a dictionary with the required parameters
        data = {
            "fanSpeed": float(fan_speed),
        }
        print(data)
        # Convert dictionary to JSON string
        json_data = json.dumps(data)

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send JSON data
            udp_socket.sendto(json_data.encode(), (self.send_to_actuator_ip, self.send_to_headwind_port))

    def send_udp_data_to_direto(self, incline_data):
        # Create a dictionary with the required parameters
        data = {
            "diretoResistance": float(incline_data),
            #"rizerIncline": float(incline_data)
        }
        print(data)
        # Convert dictionary to JSON string
        json_data = json.dumps(data)

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send JSON data
            udp_socket.sendto(json_data.encode(), (self.send_to_actuator_ip, self.send_to_direto_port))


    def stop_udp_listener(self):
        if self.udp_unity_receive_socket:
            self.udp_unity_receive_socket.close()
            print("UDP listener stopped.")



if __name__ == "__main__":
    data_sender = DataSender()

    print("Master Collector script started...")
    # IP adresses to receive data from actuators and sensors
    UDP_IP = "127.0.0.1" # IP to receive data from elite_rizer.py as well as from direto_xr.py scripts via UDP
    # UDP_IP_UNITY_RECEIVE = "127.0.0.1" # Receives Data from unity such as the ble fan data
    UDP_ESP_IP = "192.168.0.101" # IP of the computer running this script to receive data from ESP32 -> Bicycle Simulator Desktop PC
    # UDP_ESP_IP = "192.168.9.184" # Raspberry Pi 3
    # UDP_ESP_IP = "192.168.9.198" # Raspberry Pi 5

    # ports to receive data from actuators and sensors
    UDP_PORT_DIRETO = 1111
    UDP_PORT_RIZER = 2222
    UDP_PORT_ROLL = 6666
    UDP_PORT_BRAKE = 7777
    UDP_PORT_BNO = 8888
    UPD_PORT_STEERING_ANGLE = 8778
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

    udp_steering_angle_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_steering_angle_socket.bind((UDP_ESP_IP, UPD_PORT_STEERING_ANGLE))

    # udp_unity_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udp_unity_receive_socket.bind((UDP_IP_UNITY_RECEIVE, UDP_PORT_UNITY_RECEIVE))

    
    
    while True:
        # print("udp_direto_socket: ", udp_direto_socket)
        data_sender.send_unity_data_udp(data_sender.speed_value, data_sender.steering_value, data_sender.brake_value, data_sender.bno_value, data_sender.roll_value, data_sender.steering_angle)
        readable, _, _ = select.select([udp_rizer_socket, udp_direto_socket, udp_brake_socket, udp_bno_socket, udp_roll_socket, udp_steering_angle_socket], [], [])

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
                # print("BNO_Value: ", bno_value)
                bno_value = bno_value["euler_r"]
                data_sender.collect_bno(bno_value)
            elif sock is udp_roll_socket:
                roll_value = json.loads(data.decode())
                # print("Roll_Value: ", roll_value)
                roll_value = roll_value["sensor_value"]
                data_sender.collect_roll(roll_value)

            elif sock is udp_steering_angle_socket:
                steering_value = json.loads(data.decode())
                # print("Roll_Value: ", roll_value)
                steering_value = steering_value["angle"]
                data_sender.collect_steering_angle(steering_value)