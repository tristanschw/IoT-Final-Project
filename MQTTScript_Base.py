from mqttclient import MQTTClient
import network
import sys
import time
import logging
from machine import Pin



class led:
    pass

led.red = Pin(27, Pin.OUT)
led.green = Pin(12, Pin.OUT)
led.blue = Pin(13, Pin.OUT)

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



## This loop receives data from the MQTT Publisher, and Flashes the led
while True:
    ##This is a Timer

    timer = time.localtime()
    current = timestamp()
    current.year = timer[0]
    current.month = timer[1]
    current.days = timer[2]
    current.hours = timer[3]
    current.minutes = timer[4]
    current.seconds = timer[5]    
    t=0 
    def mqtt_callback(topic, msg):
        global temperature, degrees, t
        print("Connectivity Status = {} Degrees = {} Temperature = ".format(topic.decode('utf-8'), msg.decode('utf-8')))
        temperature = int(msg.decode('utf-8'))
        degrees = 20
        t=t+1
        alert_sys(degrees, temperature,t)

    # Set callback function
    mqtt.set_callback(mqtt_callback)
    # Set a topic you will subscribe too. Publish to this topic via web client and watch microcontroller recieve messages.
    mqtt.subscribe(session + "/Host")
    # Check for any messages in subscribed topics.
    mqtt.check_msg()
    time.sleep(0.1)
    
    topic_error = "{}/mcu".format(session)
    data_error = "Status: NETWORK ERROR 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
    current.month, current.year, current.hours, current.minutes, current.seconds)
    print("Sent to Main COM: '{}'".format(data_error))
    mqtt.publish(topic_error, data_error)
    time.sleep(1)
    
    def alert_sys(temperature, degrees, t):
        # Time Stamp
        topic = "{}/mcu".format(session)
        if degrees<=30 and temperature <32:
            data = "Status" + str(t) +" "+ "Nominal Readings 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            mqtt.publish(topic, data)
            print("Sent to COM: '{}'".format(data))
            t=t+1
            for _ in range(5): 
                led.green(50), led.red(0), led.blue(0)
        elif degrees>30:
            data = "Status" + str(t) +" "+ "WARNING CUT 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            print("Sent to COM: '{}'".format(data))
            mqtt.publish(topic, data)
            t=t+1
            for _ in range(5): 
                led.green(0), led.red(255), led.blue(0)
                time.sleep(0.1)
                led.green(0), led.red(255), led.blue(0)
                time.sleep(0.1)
        if degrees not in range(90):
            data = "Status" + str(t) +" "+ "NETWORK ERROR 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            mqtt.publish(topic, data)
            print("Sent to COM: '{}'".format(data))
            t=t+1
            for _ in range(5): 
                led.green(255), led.red(255), led.blue(0)
                time.sleep(0.1)
                led.green(0), led.red(0), led.blue(0)
                time.sleep(0.1)
        if temperature>32:
            data = "Status" + str(t) +" "+ "HIGH TEMPERATURE WARNING 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            print("Sent to Main COM: '{}'".format(data))
            mqtt.publish(topic, data)
            t=t+1
            for _ in range(5): 
                led.green(0), led.red(255), led.blue(0)
                time.sleep(0.1)
                led.green(0), led.red(0), led.blue(0)
                time.sleep(0.1)

# free up resources
# alternatively reset the micropyhton board before executing this program again
mqtt.disconnect()