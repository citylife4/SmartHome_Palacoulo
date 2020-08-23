import random
import socket
import datetime
import logging
import time
import os
import errno

from smarthome_relay.ArduinoConnection import HouseholdConnection
from smarthome_relay.ServerConnection import ServerThread
from smarthome_relay.ServerConnection import ClientThread
import smarthome_relay.config as config

exitFlag    = 0


class SmartHomeRelay():

    def __init__(self, logfile_path="logs/"):
    # Configure logger!
        now = datetime.datetime.now()
        #logging.basicConfig(level=logging.DEBUG, filename="logfile_" + now.strftime("%Y_%m_%d") + ".log",
        #                    filemode="a+",
        #                    format="%(asctime)-15s %(levelname)-8s %(threadName)-9s) %(message)s")
        #TODO: check follwoing
        try:
            os.makedirs(logfile_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        


        lfilename=logfile_path+"logfile_" + now.strftime("%Y_%m_%d") + ".log"

        self.logger = logging.getLogger('smarthome_relay')
        self.logger.setLevel(logging.DEBUG)
        # create file handler that logs debug and higher level messages
        fh = logging.FileHandler(lfilename)
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter("[%(asctime)s] [%(levelname)8s] --- %(message)s", "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
    
        # add the handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

        logging.addLevelName( logging.DEBUG, "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
        logging.addLevelName( logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
        logging.addLevelName( logging.WARNING, "\033[1;43m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
        logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
        

        #logging.getLogger().addHandler(logging.StreamHandler())

        # Start in a thread the ip_sender
        self.logger.info("[SmartHomerelay] Starting on "+socket.gethostname())
        # Create condition for the socket Threbbbnnmm,ads
        # condition = threading.Condition()

        # Get Threads Running
        self.clientthread = ClientThread()
        self.housoldconnection = HouseholdConnection()
        self.receiverthread = ServerThread()

        self.clientthread.start()
        self.housoldconnection.start()

        # Just so that Ip is sent first
        time.sleep(random.randrange(2, 5))  # Sleeps for some time.
        self.receiverthread.start()

        self.housoldconnection.write("<0_1_1_13_0>".encode())
        time.sleep(5)


    def run(self):
        while True:
            if not config.DOCKER:
                try:
                    cmd = input('% ')
                    if cmd[:4] == 'quit' or cmd[:4] == 'exit' :
                        self.logger.debug("[SmartHomerelay] Exiting")
                        os._exit(0)
                    if cmd[0:2] == 'S ':
                        #Send to arduino Node
                        self.logger.debug("[SmartHomerelay] Sending "+ cmd[2:])
                        self.housoldconnection.write(("<"+cmd[2:]+">").encode())
                    if cmd[0:2] == 'MD':
                        #TODO: change to send to any arduino
                        self.logger.debug("[SmartHomerelay] Sending MD")
                        MB="1_1_3_0_0"
                        self.housoldconnection.write(("<"+MB+">").encode())
                    if cmd[0:2] == 'SQ':
                        self.logger.debug("[SmartHomerelay] Server Queue: "+ str(config.SERVER_QUEUE))
                    if cmd[0:2] == 'HQ':
                        self.logger.debug("[SmartHomerelay] HouseHold Queue: "+ str(config.CLIENT_QUEUE))
                except Exception as e:
                    self.logger.debug(e)