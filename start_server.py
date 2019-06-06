import random
import socket
import datetime
import logging
import time

from arduino_connection import HouseholdConnection
from webserver_connection import ClientThread, ServerThread

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
    logging.getLogger().addHandler(logging.StreamHandler())

    # Start in a thread the ip_sender
    logging.info(socket.gethostname())
    # Create condition for the socket Threads
    # condition = threading.Condition()

    # Get Threads Running
    housoldconnection = HouseholdConnection()
    clientthread = ClientThread()
    receiverthread = ServerThread()

    # Start new Threads
    logging.info("Receiving Thread")
    housoldconnection.start()
    logging.info("IP check Thread")
    clientthread.start()

    # Just so that Ip is sent first
    time.sleep(random.randrange(2, 5))  # Sleeps for some time.
    logging.info("Door_status check Thread")
    receiverthread.start()


if __name__ == '__main__':
    main()
