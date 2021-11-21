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

# Define function to execute when a message is recieved on a subscribed topic.
def mqtt_callback(topic, msg):
    print("Connectivity Status = {} Detected Voltage Spike= {},".format(topic.decode('utf-8'), msg.decode('utf-8')))

# Set callback function
mqtt.set_callback(mqtt_callback)

# Set a topic you will subscribe too. Publish to this topic via web client and watch microcontroller recieve messages.
mqtt.subscribe(session + "/Host")

#For nominal performance
#While topic_decod.z_accel<0
#Return nominal timestamp

#if topic_decod.z_accel>0
#Return EMERGENCY timestamp

for t in range(100):
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
    data = "hello" + str(t)
    print("Nominal Readings at Timestamp: {}/{}/{}  {}/{}/{}".format(current.days,current.month,current.year,current.hours,current.minutes,current.seconds))
    mqtt.publish(topic, data)
    # Check for any messages in subscribed topics.
    for _ in range(10):
        mqtt.check_msg()
        time.sleep(0.5)

# free up resources
# alternatively reset the micropyhton board before executing this program again
mqtt.disconnect()
