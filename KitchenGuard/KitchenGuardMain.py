from KitchenGuardZ2M_Controller import KitchenGuardZ2M, KitchenGuardController
from KitchenGuardWebClient import WebClient
from threading import Thread
import time

# This function calls the safety_controller function once every five seconds
def check():
    while True:
        KitchenGuardController.safety_controller()
        time.sleep(5)

# A seperate thread is started for running the check function concurrently with the rest of the program
thread = Thread(target = check)
thread.start()

# Start MQTT client and loop, which may activate controller
KitchenGuardZ2M.start()

# Start the web client functionality, so events may be sent to database
WebClient.run()


    
