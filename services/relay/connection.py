from smarthome_proxy import SmartHomeProxy
import logging

logging.basicConfig(level=logging.DEBUG)
myclient= SmartHomeProxy.ClientThread()
myserver = SmartHomeProxy.ServerThread()

myclient.start()
myserver.start()