# MQTT_IMU
# Writtne by: Tristan Schwan and Johnathan Gilbreth
# MQTT_IMU is a program to gather sensor data from the LSM6DS0 
# The data collected is then sent to a MQTT server 
# --Server Broker -- 
#   -broker.mqttdashboard.com
# --Session Name --
#   -FallingConductor/Network


#Import required Python packages and modules
from mqttclient import MQTTClient
import network
import sys
import time
import logging
from machine import Pin
from machine import I2C
from binascii import hexlify
import math

# Connect to the MQTT Server
class timestamp:
    pass

# Session and Broker declaration
session = 'FallingConductor/Network'
BROKER = 'broker.mqttdashboard.com'

# check wifi connection and connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)

# connect to MQTT broker
print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = MQTTClient(BROKER, port='1883')
print("Connected!")


def Temperature(i2caddr):
	temperature = i2c.readfrom_mem(i2caddr,0x20,2)
	if int.from_bytes(temperature,"little") > 32767:
		temperature = int.from_bytes(temperature,"little")-65536
	else:
		temperature = int.from_bytes(temperature,"little")
	print('Temperature in Celesius: '"%4.2f" % ((temperature)/(256) + 25))
	return ((temperature)/(256) + 25)

def Zaccel(i2caddr):
	zacc = int.from_bytes(i2c.readfrom_mem(i2caddr,0x2C,2),"little")
	if zacc > 32767:
		zacc = zacc -65536
	return zacc/16393

def Xaccel(i2caddr):
	xacc = int.from_bytes(i2c.readfrom_mem(i2caddr,0x28,2),"little")
	if xacc > 32767:
		xacc = xacc -65536
	return xacc/16393
	
def Yaccel(i2caddr):
	yacc = int.from_bytes(i2c.readfrom_mem(i2caddr,0x2A,2),"little")
	if yacc > 32767:
		yacc = yacc -65536
	return yacc/16393
	
#Calculates the angel of pole from center z-axis/original position
def tilt(xacc,yacc,zacc):
	x = xacc ** 2 + yacc ** 2 + zacc **2 
	mag = math.sqrt(x)
	if mag == 0:
		tilt = 0
		print('Degrees from Upright Position: ' "%4.2f" % (tilt))
		return tilt
	tilt = math.degrees(math.acos(xacc/mag))
	print('Degrees from Upright Position: ' "%4.2f" % (tilt))
	return tilt



i2c = I2C(1,scl=Pin(22),sda=Pin(23),freq=400000)
for i in range(len(i2c.scan())):
	print(hex(i2c.scan()[i]))
buff=[0xA0]
i2c.writeto_mem(i2c.scan()[i],0x10,bytes(buff))
i2c.writeto_mem(i2c.scan()[i],0x11,bytes(buff))
time.sleep(0.1)

while True:
    #Gathers the data from the IMU sensor through the IMU_read module (IMUR)
    temp =Temperature(i2c.scan()[i])
    xacc = Xaccel(i2c.scan()[i])
    yacc = Yaccel(i2c.scan()[i])
    zacc = Zaccel(i2c.scan()[i])
    angle = tilt(xacc,yacc,zacc)
    print('_______________________________________________________')
    # Time Stamp for data being recieved
    timer= time.gmtime()
    current = timestamp()
    current.year = timer[0]
    current.month = timer[1]
    current.days = timer[2]
    current.hours = timer[3]
    current.minutes = timer[4]
    current.seconds = timer[5]

    # Microcontroller sends data to two seperate topics statements.
    topic_temp = "{}/temp".format(session)
    topic_angle = "{}/angle".format(session)
    #data = 'Angle of Pole: ' + "%4.1f" % (angle) + 'Temperature in Celsius:' + "%4.1f" % (temp)
    mess_angle = 'Angle of Power Line Pole: ' + "%4.1f" % (angle)
    mess_temp = 'Temperature in Celsius:    ' + "%4.1f" % (temp)   

    print("Network Readings from: {}/{}/{}  {}:{}:{}".format(current.days,current.month,current.year,current.hours,current.minutes,current.seconds))
    mqtt.publish(topic_angle, mess_angle)
    mqtt.publish(topic_temp, mess_temp)
    #mqtt.publish(topic,temp)
    time.sleep(2)


    
    # Check for any messages in subscribed topics.


mqtt.disconnect()