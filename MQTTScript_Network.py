from mqttclient import MQTTClient
import network
import sys
import time
import logging


class timestamp:
    pass

# Session
session = 'FallingConductor/Network'
BROKER = 'broker.mqttdashboard.com'

# check wifi connection
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

while True:
    #Time Stamp
    timer= time.gmtime()
    current = timestamp()
    current.year = timer[0]
    current.month = timer[1]
    current.days = timer[2]
    current.hours = timer[3]
    current.minutes = timer[4]
    current.seconds = timer[5]

    # Microcontroller sends hellos statements.
    topic = "{}/Host".format(session)
    data = str(degrees) + str(temperature)
    print("Network Readings from: {}/{}/{}  {}/{}/{}".format(current.days,current.month,current.year,current.hours,current.minutes,current.seconds))
    mqtt.publish(topic, data)
    # Check for any messages in subscribed topics.

# free up resources
# alternatively reset the micropyhton board before executing this program again
mqtt.disconnect()
