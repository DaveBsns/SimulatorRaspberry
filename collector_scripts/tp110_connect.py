from PyP100 import PyP100
import time

p100 = PyP100.P100("192.168.137.154", "unitylab.hhn3@gmail.com", "Unitylab") #Creates a P100 plug object

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
p100.turnOff() #Turns the connected plug off
time.sleep(5)
p100.turnOn() #Turns the connected plug on

    