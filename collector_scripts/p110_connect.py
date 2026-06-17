from PyP100 import PyP100
import time
from pathlib import Path

def read_env_file(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result

project_root_path = Path(__file__).resolve().parent.parent
env_cred = read_env_file(project_root_path / "config" / "credentials.env")
env_ip = read_env_file(project_root_path / "config" / "ip_list.env")

ip = env_ip.get("P110_IP")
username = env_cred.get("P110_USERNAME")
password = env_cred.get("P110_PASSWORD")

print(ip, username, password)

def connect_and_start_p100():
	p100 = PyP100.P100(ip, username, password) #Creates a P100 plug object
	# p100.handshake() #Creates the cookies required for further methods
	# p100.login()
	print("Restarting P100 Power Outlet")
	try:
		if(p100.get_status() == False):
			print("P100 already off")

		
		if(p100.get_status() == True):
			try:
				time.sleep(1)
				print("Waiting for devices to turn off...")
				p100.turnOff()
				time.sleep(5)
				# print("Turning on the devices...")
				# p100.turnOn()	
			except Exception:
				pass
		time.sleep(5)
		print("Turn P100 on...")
		p100.turnOn()
		time.sleep(10)	
	except Exception:
		pass
	print("done")
	return True

connect_and_start_p100()  # uncomment this if the bicycle simulator getting started by a batch or a shell script and comment it if the bicycle simulator is getting started by run.py python script
