import time
import paho.mqtt.client as mqtt
import json

# MQTT topics for powerplug and LED light
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
POWERPLUG_STATE_TOPIC = "zigbee2mqtt/StorPowerPlug"
LED_TOPIC = "zigbee2mqtt/Lampe/set"
MOTION_TOPIC_1 = "zigbee2mqtt/MotionSensor2"
MOTION_TOPIC_2 = "zigbee2mqtt/MotionSensor"

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
motion_value = 0
last_motion_value = 0
last_seen_in_kitchen = 0
last_time_sensor_check = 0
lights_on = False
illu_diff = 0
last_illu = 0
illuminance_array = []
stove_aborted = False

client = mqtt.Client()

class ctl:

    def Average(lst):
        return sum(lst) / len(lst)

    def stove_status(data):
        global stove_turned_on, stove_turned_on_timestamp
        
        if stove_aborted == False:
            if data["power"] > POWER_THRESHOLD and stove_turned_on == False:
                stove_turned_on = True
                stove_turned_on_timestamp = time.time()
                print("Stove turned on")


    def kitchen_location():
        global user_in_kitchen, user_in_room1, stove_turned_on_timestamp

        user_in_kitchen = True
        user_in_room1 = False

        print("User in kitchen")
        stove_turned_on_timestamp = time.time()

    def room1_location():
        global user_in_kitchen, user_in_room1
        user_in_kitchen = False
        user_in_room1 = True
        print("User in Room 1")

    # client, userdata
    def safety_controller():
        global stove_turned_on, stove_turned_on_timestamp, user_in_kitchen, user_in_room1, last_motion_value, last_seen_in_kitchen, last_time_sensor_check, motion_value, lights_on, stove_aborted
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
            #if data["occupancy"] == "true":
                ctl.kitchen_location()

        if msg.topic == MOTION_TOPIC_2:
            #if data["occupancy"] == "true":
                ctl.room1_location()
        
        ctl.safety_controller()


    # MQTT client setup

    client.username_pw_set("pi", "raspberry")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("raspberrypi.local", 1883, 60)

    # Start MQTT client loop
    client.loop_forever()





