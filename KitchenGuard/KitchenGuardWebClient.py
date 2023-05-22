import mysql.connector
from paho.mqtt import client as mqtt_client
import time
import json
from heucod import HeucodEvent
from datetime import datetime, timezone

# Sources of original code from this file:
# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
# https://pynative.com/python-mysql-database-connection/
# We have also reused the HEUCOD class code that was supplied in tutorial 9

class WebClient:

    # Connect the mqtt client to the raspberry pi mqtt broker
    def connect_mqtt() -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to broker")
            else:   
                print("Failed to connect", rc)

        broker = "raspberrypi.local"
        port = 1883
        client_id = f"bo"
        client = mqtt_client.Client(client_id)
        client.username_pw_set("pi", "raspberry")
        client.on_connect = on_connect
        client.connect(broker, port)

        return client

    # Publish HEUCOD event to the proper topic
    def publishEvent(client, type: str, location: str):

        topic = "zigbee2mqtt/events"    
        event = HeucodEvent()

        event.event_type = type
        event.sensor_location = location
        # Set timestamp to current time
        event.timestamp = datetime.now(tz=timezone.utc)

        result = client.publish(topic, event.to_json())

        status = result[0]
        if status == 0:
            print(f"Sent event to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    # Subscribe to events
    def subscribeToEvents(client: mqtt_client, topic: str):
        def on_message(client, userdata, msg):
            payloadJsonString = msg.payload.decode()

            print(f"Received `{msg}` from `{msg.topic}` topic")
            try:
                connection = mysql.connector.connect(host = "localhost",
                                                    database = "KitchenGuardData",
                                                    username = "root",
                                                    password = "grp4")

                event = HeucodEvent.from_json(payloadJsonString)
                
                # Storing in database
                mysql_insert_query = (f"INSERT INTO eventData(eventType, eventLocation, timestamp) VALUES ( '{event.event_type}', '{event.sensor_location}', '{event.timestamp}')")

                cursor = connection.cursor()
                cursor.execute(mysql_insert_query)
                connection.commit()

                print(cursor.rowcount, "Inserted successfully into the tables")
                
                cursor.close()

            except mysql.connector.Error as error:
                print("Failed to insert record {}".format(error))

            finally:
                if connection.is_connected():
                    connection.close()
                    print("MySql connection is closed")

        client.subscribe(topic)
        client.on_message = on_message

    # Called by the main function
    def run():
        client = WebClient.connect_mqtt()
