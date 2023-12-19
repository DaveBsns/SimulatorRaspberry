from collector_scripts.read_speed import BluetoothCallback

if __name__ == "__main__":
    # Create an instance of the BluetoothCallback class
    bluetooth_callback = BluetoothCallback()

    # Simulate data received from Bluetooth (replace this with your actual Bluetooth data)
    bluetooth_data = "Bluetooth data 1"
    bluetooth_callback.notify_callback(bluetooth_data)

    # Access the single value and print it
    received_data = bluetooth_callback.received_data
    print(f"Received data: {received_data}")