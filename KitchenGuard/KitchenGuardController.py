import paho.mqtt.client as mqtt
import json
import time

def Average(lst):
    return sum(lst) / len(lst)

# Global variables
stove_turned_on = False
stove_turned_on_timestamp = 0
user_in_kitchen = True
user_in_other_room = False
motion_value = 0
last_motion_value = 0
last_seen_in_kitchen = 0
last_time_sensor_check = 0
illuminance_array = []
last_illuminance_array = []
lights_on = False



# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MOTION_TOPIC)
    client.subscribe(POWERPLUG_STATE_TOPIC)
    client.publish(LED_TOPIC, '{"state": "OFF"}')
    client.publish(POWERPLUG_TOPIC, '{"state": "ON"}')


def on_message(client, userdata, msg):
    global stove_turned_on, stove_turned_on_timestamp, user_in_kitchen, user_in_other_room, last_motion_value, last_seen_in_kitchen, last_time_sensor_check, motion_value, lights_on

    if msg.topic == POWERPLUG_STATE_TOPIC:
        data = json.loads(msg.payload)
        if data["power"] > POWER_THRESHOLD and stove_turned_on == False:
            stove_turned_on = True
            stove_turned_on_timestamp = time.time()
            print("Stove turned on")

    if msg.topic == MOTION_TOPIC:
        data = json.loads(msg.payload)  
        illuminance_array.append(data["illuminance"])

        if time.time() >= last_time_sensor_check + 10:
            motion_value = Average(illuminance_array)
            if last_motion_value == 0:
                last_motion_value = motion_value
            print(illuminance_array)
            print(motion_value)
            illuminance_array.clear()
            if abs(motion_value - last_motion_value) > MOTION_ILLUMINANCE_THRESHOLD:
                user_in_kitchen = False
                user_in_other_room = True
                print("User in other room")
            else:
                user_in_other_room = False
                user_in_kitchen = True
                print("User in kitchen ")
                stove_turned_on_timestamp = time.time()
            last_time_sensor_check = time.time()
            last_motion_value = motion_value

    # Check if stove has been on for more than 20 minutes and user is not in kitchen
    if stove_turned_on:
        if (time.time() - stove_turned_on_timestamp > STOVE_TURN_OFF_TIME and user_in_kitchen == False):
            # Turn off stove and turn on LED light
            client.publish(POWERPLUG_TOPIC, '{"state": "OFF"}')
            client.publish(LED_TOPIC, '{"state": "ON"}')
            stove_turned_on = False
            lights_on = True
            print("Stove on and user away for more than 20 minutes, stove turned off")
            time.sleep(5)
    
    if user_in_kitchen and lights_on == True:
        client.publish(LED_TOPIC, '{"state": "OFF"}')
        lights_on = False
        print("User back in kitchen and lights disabled")

# MQTT client setup
client = mqtt.Client()
client.username_pw_set("pi", "raspberry")
client.on_connect = on_connect
client.on_message = on_message
client.connect("raspberrypi.local", 1883, 60)

# Start MQTT client loop
client.loop_forever()