from smarthome_proxy import SmartHomeProxy
import logging

logging.basicConfig(level=logging.DEBUG)
myserver = SmartHomeProxy.ClientThread()
myserver.run()