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
STOVE_TURN_OFF_TIME = 1200 # 20 minutes in seconds

# Global variables
stove_turned_on = False
stove_turned_on_timestamp = 0
user_in_kitchen = False
user_in_other_room = False
last_motion_timestamp = 0

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MOTION_TOPIC)
    client.subscribe(POWERPLUG_STATE_TOPIC)

def on_message(client, userdata, msg):
    global stove_turned_on, stove_turned_on_timestamp, user_in_kitchen, user_in_other_room, last_motion_timestamp

    if msg.topic == POWERPLUG_STATE_TOPIC:
        data = json.loads(msg.payload)
        if data["power"] > 0:
            stove_turned_on = True
            stove_turned_on_timestamp = time.time()
            #client.publish(LED_TOPIC, '{"state": "ON"}')
            print("Stove turned on")

    if msg.topic == MOTION_TOPIC:
        data = json.loads(msg.payload)
        if abs(data["illuminance"] - last_motion_timestamp) > MOTION_ILLUMINANCE_THRESHOLD:
            user_in_other_room = True
            user_in_kitchen = False
            print("User in other room")
        else:
            user_in_other_room = False
            user_in_kitchen = True
            print("User in kitchen ")
        last_motion_timestamp = data["illuminance"]

    # Check if stove has been on for more than 20 minutes and user is not in kitchen
    if stove_turned_on and time.time() - stove_turned_on_timestamp > STOVE_TURN_OFF_TIME and not user_in_kitchen:
        # Turn off stove and turn on LED light
        client.publish(POWERPLUG_TOPIC, '{"state": "OFF"}')
        client.publish(LED_TOPIC, '{"state": "ON"}')
        stove_turned_on = False
        print("Stove on and user away for more than 20 minutes")

    # Check if user has returned to kitchen and turned off stove
    if user_in_kitchen and not stove_turned_on:
        # Turn off LED light
        client.publish(LED_TOPIC, '{"state": "OFF"}')
        user_in_other_room = False
        print("User back in kitchen and stove is off")

# MQTT client setup
client = mqtt.Client()
client.username_pw_set("pi", "raspberry")
client.on_connect = on_connect
client.on_message = on_message
client.connect("raspberrypi.local", 1883, 60)

# Start MQTT client loop
client.loop_forever()
