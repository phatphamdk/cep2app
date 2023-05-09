import time


def Average(lst):
    return sum(lst) / len(lst)

class Controller:
    # Constants for motion sensor
    MOTION_TOPIC = "zigbee2mqtt/MotionSensor"
    MOTION_ILLUMINANCE_THRESHOLD = 50

    # Constants for stove turn off timer
    STOVE_TURN_OFF_TIME = 15 # in seconds, 20 minutes=1200
    POWER_THRESHOLD = 20 # in watts

    def __init__(self):
        # Global variables
        self.stove_turned_on = False
        self.stove_turned_on_timestamp = 0
        self.user_in_kitchen = True
        self.user_in_other_room = False
        self.motion_value = 0
        self.last_motion_value = 0
        self.last_seen_in_kitchen = 0
        self.last_time_sensor_check = 0
        self.illuminance_array = []
        self.last_illuminance_array = []
        self.lights_on = False

    def receive_powerplug_data(self, data):
        if data["power"] > Controller.POWER_THRESHOLD and not self.stove_turned_on:
            self.stove_turned_on = True
            self.stove_turned_on_timestamp = time.time()
            print("Stove turned on")

    def receive_motion_sensor_data(self, data):
        self.illuminance_array.append(data["illuminance"])

        if time.time() >= self.last_time_sensor_check + 10:
            self.motion_value = Average(self.illuminance_array)
            if self.last_motion_value == 0:
                self.last_motion_value = self.motion_value
            print(self.illuminance_array)
            print(self.motion_value)
            self.illuminance_array.clear()
            if abs(self.motion_value - self.last_motion_value) > Controller.MOTION_ILLUMINANCE_THRESHOLD:
                self.user_in_kitchen = False
                self.user_in_other_room = True
                print("User in other room")
            else:
                self.user_in_other_room = False
                self.user_in_kitchen = True
                print("User in kitchen ")
                self.stove_turned_on_timestamp = time.time()
            self.last_time_sensor_check = time.time()
            self.last_motion_value = self.motion_value

    def receive_led_data(self, data):
        if self.user_in_kitchen and self.lights_on:
            client.publish("zigbee2mqtt/Lampe/set", '{"state": "OFF"}')
            self.lights_on = False
            print("User back in kitchen and lights disabled")

    def turn_off_stove(self, client):
        if self.stove_turned_on:
            if (time.time() - self.stove_turned_on_timestamp > Controller.STOVE_TURN_OFF_TIME and not self.user_in_kitchen):
                # Turn off stove and turn on LED light
                client.publish("zigbee2mqtt/StorPowerPlug/set", '{"state": "OFF"}')
                client.publish("zigbee2mqtt/Lampe/set", '{"state": "ON"}')
                self.stove_turned_on = False
                self.lights_on = True
                print("Stove on and user away for more than 20 minutes, stove turned off")
                time.sleep(5)
