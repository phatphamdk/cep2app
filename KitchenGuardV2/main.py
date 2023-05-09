from controller import Controller
from zigbee2mqttclient import client

# Create a controller object
controller = Controller()

# Set the controller object for the zigbee2mqtt client to use
client.set_controller(controller)

# Start MQTT client loop
client.loop_forever()
