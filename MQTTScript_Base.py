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
    
    topic_temp = "{}/temp".format(session)
    topic_angle = "{}/angle".format(session)
    toc = "{}".format(session)
    
    def mqtt_callback(topic_angle, msg):
        global temperature, degrees, t
        print("Status = {}, {}".format(topic_angle.decode('utf-8'), msg.decode('utf-8')))
        if topic_angle.decode('utf-8') == "{}/angle".format(session):
            message = msg.decode('utf-8')
            slice = message[len(message)-4:len(message)]
            angle = float(slice)
            t=t+1
            alert_sys_angle(angle,t)
        if topic_angle.decode('utf-8') == "{}/temp".format(session):
            message = msg.decode('utf-8')
            slice = message[len(message)-4:len(message)]
            temp = float(slice)
            t=t+1
            alert_sys_temp(temp,t)

    # Set callback function
    mqtt.set_callback(mqtt_callback)
    # Set a topic you will subscribe too. Publish to this topic via web client and watch microcontroller recieve messages.
    mqtt.subscribe(topic_angle)
    mqtt.subscribe(topic_temp)

    # Check for any messages in subscribed topics.
    mqtt.check_msg()
    time.sleep(1)
    
    topic_error = "{}/mcu".format(session)
    data_error = "Status: NETWORK ERROR NO DATA RECEIVED 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
    current.month, current.year, current.hours, current.minutes, current.seconds)
    print("Sent to Main COM: '{}'".format(data_error))
    mqtt.publish(topic_error, data_error)
    time.sleep(1)
    led.green(0), led.red(0), led.blue(255)
    #Function that defines the LED Alert System
    def alert_sys_angle(degrees, t):
        topic = "{}/mcu".format(session)
        if degrees<30:
            data = "Status" + str(t) +" "+ "Nominal Readings 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            mqtt.publish(topic, data)
            print("Sent to COM: '{}'".format(data))
            t=t+1 
            led.green(50), led.red(0), led.blue(0)
            time.sleep(.7)
        elif degrees>30:
            data = "Status" + str(t) +" "+ "WARNING CUT 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
            current.month, current.year, current.hours, current.minutes, current.seconds)
            print("Sent to COM: '{}'".format(data))
            mqtt.publish(topic, data)
            t=t+1
            for _ in range(5): 
                led.green(0), led.red(255), led.blue(0)
                time.sleep(0.6)
                led.green(0), led.red(0), led.blue(0)
                time.sleep(0.6)

    def alert_sys_temp(temperature, t):
        topic = "{}/mcu".format(session)
        if temperature <28:
            data = "Status" + str(t) +" "+ "Nominal Readings 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            mqtt.publish(topic, data)
            print("Sent to COM: '{}'".format(data))
            t=t+1
            led.green(255), led.red(0), led.blue(0)
            time.sleep(.7)
        if temperature>28:
            data = "Status" + str(t) +" "+ "HIGH TEMPERATURE WARNING 61.12.23: {}/{}/{} Received: {}:{}:{}".format(current.days,
              current.month, current.year, current.hours, current.minutes, current.seconds)
            print("Sent to Main COM: '{}'".format(data))
            mqtt.publish(topic, data)
            t=t+1
            for _ in range(5): 
                led.green(255), led.red(255), led.blue(0)
                time.sleep(0.6)
                led.green(0), led.red(0), led.blue(0)
                time.sleep(0.6)

# free up resources
# alternatively reset the micropyhton board before executing this program again
mqtt.disconnect()