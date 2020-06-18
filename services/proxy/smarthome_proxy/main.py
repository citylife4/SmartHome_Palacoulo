import random
import socket
import datetime
import logging
import time

from HouseholdConnection import HouseholdConnection
from ServerConnection import ServerConnection
from ServerConnection import ClientThread

exitFlag    = 0


def main():
    # Configure logger!
    now = datetime.datetime.now()
    logging.basicConfig(level=logging.DEBUG, filename="/home/jdv/logfiles/logfile_" + now.strftime("%Y_%m_%d") + ".log",
                        filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(threadName)-9s) %(message)s")
    stderrLogger = logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(stderrLogger)
    #logging.getLogger().addHandler(logging.StreamHandler())

    # Start in a thread the ip_sender
    logging.info(socket.gethostname())
    # Create condition for the socket Threbbbnnmm,ads
    # condition = threading.Condition()

    # Get Threads Running
    clientthread = ClientThread()
    housoldconnection = HouseholdConnection()
    receiverthread = ServerConnection()

    logging.info("IP check Thread")
    #clientthread.start()
    # Start new Threads
    logging.info("Receiving Thread")
    housoldconnection.start()


    # Just so that Ip is sent first
    time.sleep(random.randrange(2, 5))  # Sleeps for some time.
    logging.info("Door_status check Thread")
    receiverthread.start()

    housoldconnection.write("<0_1_1_13_1>".encode())
    time.sleep(5)
    #housoldconnection.write("<0_1_1_9_0>".encode())
    #housoldconnection.write("<0_1_1_8_1>".encode())
    #time.sleep(5)
    #housoldconnection.write("<0_1_1_8_0>".encode())


if __name__ == '__main__':
    main()
