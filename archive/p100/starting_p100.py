from PyP100 import PyP100
import time

'''
Restarting the tapo p100 plug via python to start the bicycle simulator
'''
p100 = PyP100.P100("192.168.9.173", "unitylab.hhn3@gmail.com", "Unitylab")
# p100.handshake() # deprecated
# p100.login() # deprecated
p100.turnOff()
time.sleep(5)
p100.turnOn()
