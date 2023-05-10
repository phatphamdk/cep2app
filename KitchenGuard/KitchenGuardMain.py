from KitchenGuardZ2M_Controller import KitchenGuardZ2M
from KitchenGuardWebClient import WebClient

# Start MQTT client and loop, which may activate controller
KitchenGuardZ2M.start()


WebClient.run()



