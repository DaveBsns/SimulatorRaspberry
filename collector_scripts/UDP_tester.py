import socket
import json

def send_udp_data(ip, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        # Konvertiere die Ganzzahl in Bytes
        data_bytes = str(data).encode()
        udp_socket.sendto(data_bytes, (ip, port))
        print(f"Gesendete Nachricht: {data} an {ip}:{port}")

def send_udp_json_data(ip, port, data):
        
        json_data = {
            "fanSpeed": float(data),
        }
        print(json_data)
        # Convert dictionary to JSON string
        json_data = json.dumps(json_data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Konvertiere die Ganzzahl in Bytes
            data_bytes = str(json_data).encode()
            udp_socket.sendto(data_bytes, (ip, port))
            print(f"Gesendete Nachricht: {data} an {ip}:{port}")


# Beispiel für die Nutzung der Funktion
if __name__ == "__main__":
    # Eingaben vom Benutzer einholen
    if input("rizer? ") == ("y"):
        incline = int(input("incline "))
        send_udp_data("127.0.0.3", 2223, incline)
    else:
        ip = input("Geben Sie die IP-Adresse des Empfängers ein: ")
        port = int(input("Geben Sie den Port des Empfängers ein: "))
        data = int(input("Geben Sie die zu sendende Ganzzahl ein: "))
        # UDP-Daten senden
        send_udp_json_data(ip, port, data)