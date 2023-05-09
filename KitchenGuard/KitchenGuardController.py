import time
import paho.mqtt.client as mqtt
import json

# MQTT topics for powerplug and LED light
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
POWERPLUG_STATE_TOPIC = "zigbee2mqtt/StorPowerPlug"
LED_TOPIC = "zigbee2mqtt/Lampe/set"
MOTION_TOPIC_1 = "zigbee2mqtt/MotionSensor2"
MOTION_TOPIC_2 = "zigbee2mqtt/MotionSensor"
MOTION_TOPIC_3 = "zigbee2mqtt/MotionSensor3"
MOTION_TOPIC_4 = "zigbee2mqtt/MotionSensor4"
MOTION_TOPIC_5 = "zigbee2mqtt/MotionSensor5"

# Constants for motion sensor
MOTION_ILLUMINANCE_THRESHOLD = 50

# Constants for stove turn off timer
STOVE_TURN_OFF_TIME = 15 # in seconds, 20 minutes=1200
POWER_THRESHOLD = 20 # in watts

# Global variables
stove_turned_on = False
stove_turned_on_timestamp = 0
user_in_kitchen = True
user_in_room1 = False
user_in_room2 = False
user_in_room3 = False
user_in_room4 = False
lights_on = False
stove_aborted = False

client = mqtt.Client()

class ctl:

    def stove_status(data):
        global stove_turned_on, stove_turned_on_timestamp, stove_aborted
        
        if stove_aborted == False:
            if data["power"] > POWER_THRESHOLD and stove_turned_on == False:
                stove_turned_on = True
                stove_turned_on_timestamp = time.time()
                print("Stove turned on")


    def user_location(room):
        global user_in_kitchen, user_in_room1, user_in_room2, user_in_room3, user_in_room4, stove_turned_on_timestamp

        if room == 1:
            user_in_room1 = True
            user_in_room2 = False
            user_in_room3 = False
            user_in_room4 = False
            user_in_kitchen = False
            print("User in Room 1")

        if room == 2:
            user_in_room1 = False
            user_in_room2 = True
            user_in_room3 = False
            user_in_room4 = False
            user_in_kitchen = False
            print("User in Room 2")

        if room == 3:
            user_in_room1 = False
            user_in_room2 = False
            user_in_room3 = True
            user_in_room4 = False
            user_in_kitchen = False
            print("User in Room 3")

        if room == 4:
            user_in_room1 = False
            user_in_room2 = False
            user_in_room3 = False
            user_in_room4 = True
            user_in_kitchen = False
            print("User in Room 4")

        if room == 5:
            user_in_room1 = False
            user_in_room2 = False
            user_in_room3 = False
            user_in_room4 = False
            user_in_kitchen = True

            print("User in kitchen")
            stove_turned_on_timestamp = time.time()


    # client, userdata
    def safety_controller():
        global stove_turned_on, stove_turned_on_timestamp, user_in_kitchen, lights_on, stove_aborted
        # Check if stove has been on for more than 20 minutes and user is not in kitchen
        if stove_turned_on == True:
            if (time.time() - stove_turned_on_timestamp > STOVE_TURN_OFF_TIME and user_in_kitchen == False):
                # Turn off stove and turn on LED light
                stove_aborted = True
                client.publish(POWERPLUG_TOPIC, '{"state": "OFF"}')
                client.publish(LED_TOPIC, '{"state": "ON"}')
                stove_turned_on = False
                lights_on = True
                print("Stove on and user away for more than 20 minutes, stove turned off")
                time.sleep(10)
        
        if user_in_kitchen and lights_on == True:
            client.publish(LED_TOPIC, '{"state": "OFF"}')
            lights_on = False
            print("User back in kitchen and lights disabled")

class kgz2m:

     # MQTT client callbacks
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(MOTION_TOPIC_1)
        client.subscribe(MOTION_TOPIC_2)
        client.subscribe(POWERPLUG_STATE_TOPIC)
        client.publish(LED_TOPIC, '{"state": "OFF"}')
        client.publish(POWERPLUG_TOPIC, '{"state": "ON"}')


    def on_message(client, userdata, msg):
        
        data = json.loads(msg.payload)

        if msg.topic == POWERPLUG_STATE_TOPIC:
            ctl.stove_status(data)

        if msg.topic == MOTION_TOPIC_1:
            if data["occupancy"] == True:
                ctl.user_location(1)

        if msg.topic == MOTION_TOPIC_2:
            if data["occupancy"] == True:
                ctl.user_location(2)

        if msg.topic == MOTION_TOPIC_3:
            if data["occupancy"] == True:
                ctl.user_location(3)
        
        if msg.topic == MOTION_TOPIC_4:
            if data["occupancy"] == True:
                ctl.user_location(4)

        if msg.topic == MOTION_TOPIC_5:
            if data["occupancy"] == True:
                ctl.user_location(5)

        ctl.safety_controller()


    # MQTT client setup

    client.username_pw_set("pi", "raspberry")
    client.on_connect = on_connect
    client.on_message = on_message

    def start():
        # Start MQTT client loop
        client.connect("raspberrypi.local", 1883, 60)
        client.loop_forever()





