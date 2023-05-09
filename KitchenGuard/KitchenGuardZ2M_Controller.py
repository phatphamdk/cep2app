import time
import paho.mqtt.client as mqtt
import json
from KitchenGuardWebClient import Events

# MQTT topics for powerplug and LED light
POWERPLUG_TOPIC = "zigbee2mqtt/StorPowerPlug/set"
POWERPLUG_STATE_TOPIC = "zigbee2mqtt/StorPowerPlug"
LED_TOPIC_1 = "zigbee2mqtt/Lampe1/set" #ændre til rigtig
LED_TOPIC_2 = "zigbee2mqtt/Lampe2/set"#ændre til rigtig
LED_TOPIC_3 = "zigbee2mqtt/Lampe3/set"#ændre til rigtig
LED_TOPIC_4 = "zigbee2mqtt/Lampe4/set"#ændre til rigtig
MOTION_TOPIC_1 = "zigbee2mqtt/MotionSensor1"#ændre til rigtig
MOTION_TOPIC_2 = "zigbee2mqtt/MotionSensor2"#ændre til rigtig
MOTION_TOPIC_3 = "zigbee2mqtt/MotionSensor3"#ændre til rigtig
MOTION_TOPIC_4 = "zigbee2mqtt/MotionSensor4"#ændre til rigtig
MOTION_TOPIC_KITCHEN = "zigbee2mqtt/MotionSensorKitchen"#ændre til rigtig

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
light_on = False
light_on_1 = False
light_on_2 = False
light_on_3 = False
light_on_4 = False
stove_aborted = False
last_seen_in_kitchen = 0


client = mqtt.Client()

class KitchenGuardController:

    # This function determines whether or not the stove is turned on, and notes the time when it is turned on
    def stove_status(data):
        global stove_turned_on, stove_turned_on_timestamp, stove_aborted
        
        if stove_aborted == False:
            if data["power"] > POWER_THRESHOLD and stove_turned_on == False:
                stove_turned_on = True
                stove_turned_on_timestamp = time.time()
                print("Stove turned on")
                

    # This function determines where the user is located. 
    def user_location(room):
        global user_in_kitchen, user_in_room1, user_in_room2, user_in_room3, user_in_room4, stove_turned_on_timestamp, last_seen_in_kitchen
        
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
            # The timestamp of when the user is last seen in the kitchen is updated.
            last_seen_in_kitchen = time.time()


    #This function determines whether or not the stove must be turned off, and the lights turned on or off
    def safety_controller():
        global stove_turned_on, stove_turned_on_timestamp, user_in_kitchen, light_on, light_on_1, light_on_2, light_on_3, light_on_4,stove_aborted
        # Check if stove has been on for more than 20 minutes and user is not in kitchen
        if stove_turned_on == True:
            if (time.time() - last_seen_in_kitchen > STOVE_TURN_OFF_TIME and user_in_kitchen == False):
                # Turn off stove and turn on LED light
                stove_aborted = True
                client.publish(POWERPLUG_TOPIC, '{"state": "OFF"}')
                if user_in_room1:
                    client.publish(LED_TOPIC_1, '{"state": "ON"}')
                    light_on_1 = True
                elif user_in_room2:  
                    client.publish(LED_TOPIC_2, '{"state": "ON"}')
                    light_on_2 = True
                elif user_in_room3:  
                    client.publish(LED_TOPIC_3, '{"state": "ON"}')
                    light_on_3 = True
                elif user_in_room4:  
                    client.publish(LED_TOPIC_4, '{"state": "ON"}')
                    light_on_4 = True
                stove_turned_on = False
                light_on = True
                print("Stove on and user away for more than 20 minutes, stove turned off")
                time.sleep(10)
        
        # Turn off lights if user has returned to kitchen.
        if user_in_kitchen and light_on == True:
            if user_in_room1:
                client.publish(LED_TOPIC_1, '{"state": "OFF"}')
                light_on_1 = False
            elif user_in_room2:  
                client.publish(LED_TOPIC_2, '{"state": "OFF"}')
                light_on_2 = False
            elif user_in_room3:  
                client.publish(LED_TOPIC_3, '{"state": "OFF"}')
                light_on_3 = False
            elif user_in_room4:  
                client.publish(LED_TOPIC_4, '{"state": "OFF"}')
                light_on_4 = False

            light_on = False
            print("User back in kitchen and lights disabled")

class KitchenGuardZ2M:

     # MQTT client callbacks
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(MOTION_TOPIC_1)
        client.subscribe(MOTION_TOPIC_2)
        client.subscribe(MOTION_TOPIC_3)
        client.subscribe(MOTION_TOPIC_4)
        client.subscribe(MOTION_TOPIC_KITCHEN)
        client.subscribe(POWERPLUG_STATE_TOPIC)
        client.publish(LED_TOPIC_1, '{"state": "OFF"}')
        client.publish(POWERPLUG_TOPIC, '{"state": "ON"}')


    # Handle MQTT message received by called other functions depending on which message is received.
    def on_message(client, userdata, msg):
        
        data = json.loads(msg.payload)

        if msg.topic == POWERPLUG_STATE_TOPIC:
            KitchenGuardController.stove_status(data)

        if msg.topic == MOTION_TOPIC_1:
            if data["occupancy"] == True:
                KitchenGuardController.user_location(1)

        if msg.topic == MOTION_TOPIC_2:
            if data["occupancy"] == True:
                KitchenGuardController.user_location(2)

        if msg.topic == MOTION_TOPIC_3:
            if data["occupancy"] == True:
                KitchenGuardController.user_location(3)
        
        if msg.topic == MOTION_TOPIC_4:
            if data["occupancy"] == True:
                KitchenGuardController.user_location(4)

        if msg.topic == MOTION_TOPIC_KITCHEN:
            if data["occupancy"] == True:
                KitchenGuardController.user_location(5)

        # Call safety_controller function each time a message is received. 
        KitchenGuardController.safety_controller()


    # MQTT client setup
    client.username_pw_set("pi", "raspberry")
    client.on_connect = on_connect
    client.on_message = on_message

    def start():
        # Start MQTT client loop
        client.connect("raspberrypi.local", 1883, 60)
        client.loop_forever()





