class DataCollection:
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