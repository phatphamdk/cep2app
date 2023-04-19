import paho.mqtt.client as mqtt
import json
import time

# MQTT topics for powerplug and LED light
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
POWERPLUG_STATE_TOPIC = "zigbee2mqtt/StorPowerPlug"
LED_TOPIC = "zigbee2mqtt/Lampe/set"

# Constants for motion sensor
MOTION_TOPIC = "zigbee2mqtt/MotionSensor"
MOTION_ILLUMINANCE_THRESHOLD = 100

# Constants for stove turn off timer
STOVE_TURN_OFF_TIME = 15 # in seconds, 20 minutes=1200
POWER_THRESHOLD = 20 # in watts

# Global variables
stove_turned_on = False
stove_turned_on_timestamp = 0
user_in_kitchen = False
user_in_other_room = False
last_motion_value = 0
last_seen_in_kitchen = 0
last_time_sensor_check = 0

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MOTION_TOPIC)
    client.subscribe(POWERPLUG_STATE_TOPIC)

def on_message(client, userdata, msg):
    global stove_turned_on, stove_turned_on_timestamp, user_in_kitchen, user_in_other_room, last_motion_value, last_seen_in_kitchen, last_time_sensor_check

    if msg.topic == POWERPLUG_STATE_TOPIC:
        data = json.loads(msg.payload)
        if data["power"] > POWER_THRESHOLD:
            stove_turned_on = True
            stove_turned_on_timestamp = time.time()
            #client.publish(LED_TOPIC, '{"state": "ON"}')
            if user_in_kitchen:
                 last_seen_in_kitchen = stove_turned_on_timestamp
            print("Stove turned on")

    if msg.topic == MOTION_TOPIC:
        data = json.loads(msg.payload)
        
        if time.time() >= last_time_sensor_check + 5:
            if abs(data["illuminance"] - last_motion_value) > MOTION_ILLUMINANCE_THRESHOLD and not last_motion_value == 0:
                user_in_kitchen = False
                print("User in other room")
                last_time_sensor_check = time.time()
            else:
                user_in_other_room = False
                user_in_kitchen = True
                print("User in kitchen ")
                last_time_sensor_check = time.time()
            last_motion_value = data["illuminance"]

    # Check if stove has been on for more than 20 minutes and user is not in kitchen
    if stove_turned_on:
        if (time.time() - stove_turned_on_timestamp > STOVE_TURN_OFF_TIME):
            # Turn off stove and turn on LED light
            client.publish(POWERPLUG_TOPIC, '{"state": "OFF"}')
            client.publish(LED_TOPIC, '{"state": "ON"}')
            stove_turned_on = False
            print("Stove on and user away for more than 20 minutes, stove turned off")
            if user_in_kitchen:
                client.publish(LED_TOPIC, '{"state": "OFF"}')
                print("User back in kitchen and lights disabled")


    

# MQTT client setup
client = mqtt.Client()
client.username_pw_set("pi", "raspberry")
client.on_connect = on_connect
client.on_message = on_message
client.connect("raspberrypi.local", 1883, 60)

# Start MQTT client loop
client.loop_forever()