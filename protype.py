import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("zigbee2mqtt/MotionSensor")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "zigbee2mqtt/bridge/MotionSensor":
        data = json.loads(msg.payload)
        illuminance = data["illuminance"]
        illuminance_lux = data["illuminance_lux"]
        linkquality = data["linkquality"]
        occupancy = data["occupancy"]
        print("Illuminance:", illuminance)
        print("Illuminance Lux:", illuminance_lux)
        print("Link Quality:", linkquality)
        print("Occupancy:", occupancy)

client = mqtt.Client()
client.username_pw_set("pi", "raspberry")
client.on_connect = on_connect
client.on_message = on_message

client.connect("raspberrypi.local", 1883, 60)

client.loop_forever()