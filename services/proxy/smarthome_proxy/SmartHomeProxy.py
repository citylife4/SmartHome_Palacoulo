import random
import socket
import datetime
import logging
import time
import os

from smarthome_proxy.ArduinoConnection import HouseholdConnection
from smarthome_proxy.ServerConnection import ServerConnection
from smarthome_proxy.ServerConnection import ClientThread
import smarthome_proxy.config as config

exitFlag    = 0


class SmartHomeProxy():

    def __init__(self):
    # Configure logger!
        now = datetime.datetime.now()
        #logging.basicConfig(level=logging.DEBUG, filename="logfile_" + now.strftime("%Y_%m_%d") + ".log",
        #                    filemode="a+",
        #                    format="%(asctime)-15s %(levelname)-8s %(threadName)-9s) %(message)s")
        logging.basicConfig(level=logging.DEBUG)
        stderrLogger = logging.StreamHandler()
        stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logging.getLogger().addHandler(stderrLogger)
        #logging.getLogger().addHandler(logging.StreamHandler())

        # Start in a thread the ip_sender
        logging.info(socket.gethostname())
        # Create condition for the socket Threbbbnnmm,ads
        # condition = threading.Condition()

        # Get Threads Running
        self.clientthread = ClientThread()
        self.housoldconnection = HouseholdConnection()
        self.receiverthread = ServerConnection()

        logging.info("IP check Thread")
        #clientthread.start()
        # Start new Threads
        logging.info("Receiving Thread")
        self.housoldconnection.start()


        # Just so that Ip is sent first
        time.sleep(random.randrange(2, 5))  # Sleeps for some time.
        logging.info("Door_status check Thread")
        self.receiverthread.start()

        self.housoldconnection.write("<0_1_1_13_0>".encode())
        time.sleep(5)


    def run(self):
        while True:
            if not config.DOCKER:
                try:
                    cmd = input('% ')
                    if cmd[:4] == 'quit':
                        print("Exiting")
                        os._exit(0)
                    if cmd[0:2] == 'S ':
                        #Send to arduino Node
                        print("Sending "+ cmd[2:])
                        self.housoldconnection.write(("<"+cmd[2:]+">").encode())
                    if cmd[0:2] == 'SQ':
                        print("Server Queue: ", config.SERVER_QUEUE)
                    if cmd[0:2] == 'HQ':
                        print("HouseHold Queue: ", config.HOUSEHOLDE_QUEUE)
                except Exception as e:
                    print(e)
