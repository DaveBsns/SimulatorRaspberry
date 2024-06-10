from master_collector import DataReceiver

class DataReceiverSingleton:
  _instance = None
  _receiver = None  # Neue Variable zur Speicherung der DataReceiver-Instanz

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    if cls._receiver is None:
      cls._receiver = DataReceiver()  # Erstelle die DataReceiver-Instanz beim ersten Aufruf
    return cls._instance