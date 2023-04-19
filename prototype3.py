import paho.mqtt.client as mqtt
import json
import time

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set("pi", "raspberry")
client.connect("raspberrypi.local", 1883, 60)

# Set up topic names
MOTION_SENSOR_TOPIC = "zigbee2mqtt/MotionSensor"
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
POWERPLUG_STATE_TOPIC = "zigbee2mqtt/StorPowerPlug"
LED_LIGHT_TOPIC = "zigbee2mqtt/Lampe/set"

# Set up variables
motion_detected = False
stove_turned_on = False
start_time = 0
prev_illuminance = 0
#inital state on system startup


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MOTION_SENSOR_TOPIC)
    client.subscribe(POWERPLUG_STATE_TOPIC)

def on_message(client, userdata, msg):
    global motion_detected
    global stove_turned_on
    global start_time
    
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == MOTION_SENSOR_TOPIC:
        data = json.loads(msg.payload)
        illuminance = data["illuminance"]
        if abs(illuminance - prev_illuminance) >= 100:
            motion_detected = True
            print("Motion detected!")
    if msg.topic == POWERPLUG_STATE_TOPIC:
        data = json.loads(msg.payload)
        power = data["power"]
        if power >= 20:
            stove_turned_on = True
            start_time = time.time()
            print("Stove turned on!")
    
    prev_illuminance = illuminance

client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

# Main loop
while True:
    if stove_turned_on:
        if motion_detected:
            # User has left the kitchen
            if time.time() - start_time > 1200:
                # Stove has been on for more than 20 minutes, turn it off
                client.publish(POWERPLUG_TOPIC, payload=json.dumps({"state": "OFF"}), qos=0, retain=False)
                client.publish(LED_LIGHT_TOPIC, payload=json.dumps({"state": "ON"}), qos=0, retain=False)
                print("Stove turned off!")
            else:
                # User has been away for less than 20 minutes, check again in 1 minute
                time.sleep(60)
        else:
            # User has returned to the kitchen
            client.publish(LED_LIGHT_TOPIC, payload=json.dumps({"state": "OFF"}), qos=0, retain=False)
            motion_detected = False
            stove_turned_on = False
            print("User in kitchen!")
    else:
        # Stove is turned off, check again in 1 minute
        time.sleep(60)
