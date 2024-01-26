from PyP100 import PyP100
import time


def connect_and_start_p100():
	p100 = PyP100.P100("192.168.9.173", "unitylab.hhn3@gmail.com", "Unitylab") #Creates a P100 plug object
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
		time.sleep(1)
		print("Turn P100 on...")
		p100.turnOn()
		time.sleep(5)	
	except Exception:
		pass
	print("done")
	return True

# connect_and_start_p100()

