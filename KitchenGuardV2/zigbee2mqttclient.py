import paho.mqtt.client as mqtt
from controller import Controller
import json

# MQTT topics for powerplug and LED light
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
LED_TOPIC = "zigbee2mqtt/Lampe/set"

# Create a controller object
controller = Controller()

# MQTT client setup
client = mqtt.Client()
client.username_pw_set("pi", "raspberry")
client.connect("raspberrypi.local", 1883, 60)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    if msg.topic == POWERPLUG_TOPIC:
        # Send powerplug data to controller
        controller.receive_powerplug_data(data)
    elif msg.topic == LED_TOPIC:
        # Send LED data to controller
        controller.receive_led_data(data)

# MQTT client callbacks
client.on_message = on_message

# Set the controller object for the zigbee2mqtt client to use
client.controller = controller

# Start MQTT client loop
client.loop_forever()
