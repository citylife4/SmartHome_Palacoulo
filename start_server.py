import random
import socket
import datetime
import logging
import threading
import time

from requests import get

from arduino_connection.arduino_connection import HouseholdConnection
from webserver_connection import webserver_connection
from webserver_connection.webserver_connection import send_socket, ReceiveThread

exitFlag    = 0
IPWAITTIME  = 10


class IPThread(threading.Thread):
    def __init__(self, condition):
        threading.Thread.__init__(self)
        self.condition = condition
        self.my_address = get('https://ipapi.co/ip/').text
        self.packet_id = "ip"
        to_send = "{}_{}".format(self.packet_id, self.my_address)
        logging.info("First IP sent to host")
        with condition:
            send_socket(str(to_send))

    def run(self):
        logging.info("Starting " + self.name)
        while 1:
            new_address = get('https://ipapi.co/ip/').text
            if self.my_address is new_address:
                self.my_address = new_address
                with self.condition:
                    to_send = "{}_{}".format(self.packet_id, new_address)
                    send_socket(str(to_send))
            time.sleep(IPWAITTIME)


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
    condition = threading.Condition()

    # Get Threads Running
    thread1 = HouseholdConnection()
    thread2 = IPThread(condition)
    thread3 = ReceiveThread()

    # Start new Threads
    logging.info("Receiving Thread")
    thread1.start()
    logging.info("IP check Thread")
    thread2.start()

    # Just so that Ip is sent first
    time.sleep(random.randrange(2, 5))  # Sleeps for some time.
    logging.info("Door_status check Thread")
    thread3.start()


if __name__ == '__main__':
    main()
