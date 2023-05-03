from KitchenGuardController import ctl
import paho.mqtt.client as mqtt
import json
import time

# MQTT topics for powerplug and LED light
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
POWERPLUG_STATE_TOPIC = "zigbee2mqtt/StorPowerPlug"
LED_TOPIC = "zigbee2mqtt/Lampe/set"
MOTION_TOPIC_1 = "zigbee2mqtt/MotionSensor2"
MOTION_TOPIC_2 = "zigbee2mqtt/MotionSensor"

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
    client = mqtt.Client()
    client.username_pw_set("pi", "raspberry")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("raspberrypi.local", 1883, 60)

    # Start MQTT client loop
    client.loop_forever()


