from master_collector import DataReceiver

class DataReceiverSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataReceiverSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        print("Instance created")