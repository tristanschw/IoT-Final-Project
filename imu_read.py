from machine import Pin
from machine import I2C
from binascii import hexlify
import time
import math


i2c = I2C(1,scl=Pin(22),sda=Pin(23),freq=400000)

# zacc = []
# xacc = []
# yacc = []

for i in range(len(i2c.scan())):
 	print(hex(i2c.scan()[i]))

def WHOAMI(i2caddr):
	whoami = i2c.readfrom_mem(i2caddr,0x0F,1)
	print(hex(int.from_bytes(whoami,"little")))

def Temperature(i2caddr):
	temperature = i2c.readfrom_mem(i2caddr,0x20,2)
	if int.from_bytes(temperature,"little") > 32767:
		temperature = int.from_bytes(temperature,"little")-65536
	else:
		temperature = int.from_bytes(temperature,"little")
	print('Temperature in Celesius: '"%4.2f" % ((temperature)/(256) + 25))

def Zaccel(i2caddr):
	zacc = int.from_bytes(i2c.readfrom_mem(i2caddr,0x2C,2),"little")
	if zacc > 32767:
		zacc = zacc -65536
	print('Z-Accceleration: '"%4.2f"'g' % (zacc/16393))
	return zacc/16393

def Xaccel(i2caddr):
	xacc = int.from_bytes(i2c.readfrom_mem(i2caddr,0x28,2),"little")
	if xacc > 32767:
		xacc = xacc -65536
	print('X-Accceleration: '"%4.2f"'g' % (xacc/16393))
	return xacc/16393

def Yaccel(i2caddr):
	yacc = int.from_bytes(i2c.readfrom_mem(i2caddr,0x2A,2),"little")
	if yacc > 32767:
		yacc = yacc -65536
	print('Y-Accceleration: '"%4.2f""g" % (yacc/16393))
	return yacc/16393

def tilt(xacc,yacc,zacc):
    x = xacc ** 2 + yacc ** 2 + zacc **2 
    mag = math.sqrt(x)
    tilt = math.degrees(math.acos(xacc/mag))
    print('Degrees from Upright Position: ' "%4.2f" % (tilt))
    return tilt


buff=[0xA0]
i2c.writeto_mem(i2c.scan()[i],0x10,bytes(buff))
i2c.writeto_mem(i2c.scan()[i],0x11,bytes(buff))
time.sleep(0.1)

try:
	while(1):
		#WHOAMI(i2c.scan()[i])
		Temperature(i2c.scan()[i])
		xacc = Xaccel(i2c.scan()[i])
		yacc = Yaccel(i2c.scan()[i])
		zacc = Zaccel(i2c.scan()[i])
		degree = tilt(xacc,yacc,zacc)
		time.sleep(1)

except KeyboardInterrupt:
	i2c.deinit()
	pass
