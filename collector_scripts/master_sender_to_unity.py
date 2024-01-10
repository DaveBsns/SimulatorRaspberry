import socket
import json
import time
import master_collector

if __name__ == "__main__":
    # data_collector = DataCollection()
    print("Master Sender to unity script started...")

    # IP adresses to receive data from actuators and sensors
    UDP_UNITY_IP = "127.0.0.2"

    # ports to receive data from actuators and sensors
    UDP_UNITY_PORT = 1337

    

    def send_steering_data_udp(speed_data, steering_data, brake_data, bno_data, roll_data):
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
            udp_socket.sendto(json_data.encode(), (UDP_UNITY_IP, UDP_UNITY_PORT))

    while True:
        
        speed = data_collector.speed_value
        steering = data_collector.steering_value
        bno = data_collector.bno_value
        brake = data_collector.brake_value
        # roll = data_collector.roll_value
        
        '''
        # Example usage:
        speed = master_collector.get_speed()
        steering = 30
        bno = 60
        brake = 20
        roll = 50
        '''

        print(f"Speed: {speed}, Steering: {steering}, BNO: {bno}, Brake: {brake}")


        send_steering_data_udp(speed, steering, brake, bno, 0)
        
        time.sleep(1)



