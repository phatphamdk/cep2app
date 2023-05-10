from KitchenGuardZ2M_Controller import KitchenGuardZ2M, KitchenGuardController
from KitchenGuardWebClient import WebClient
from threading import Thread
import time


def check():
    while True:
        KitchenGuardController.safety_controller()
        time.sleep(5)

thread = Thread(target = check)

thread.start()

# Start MQTT client and loop, which may activate controller
KitchenGuardZ2M.start()


WebClient.run()


    
