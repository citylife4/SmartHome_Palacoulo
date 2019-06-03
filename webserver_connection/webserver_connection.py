import socket
import time
from threading import Thread

import webserver_connection.webserver_protocol as protocol
import logging
from requests import get
from config import interface, FOR_RASP


# create the connection and check if something is getting through
class ReceiveThread(Thread):
    def __init__(self, host='', port=4662):
        super(ReceiveThread,self).__init__()

        self.connection = None
        self.server = socket.socket(
            socket.AF_INET
            , socket.SOCK_STREAM
        )
        self.server.setsockopt(
            socket.SOL_SOCKET
            , socket.SO_REUSEADDR
            , 1
        )
        self.server.bind((host,port))
        self.server.listen(1)

    def run(self):
        logging.info("ReceiveThread Thread - Starting ")
        #socket_connection.socker_bind_connection()
        while 1:
            #connection can terminate at anytime
            #Try catch??
            connection, addr = self.server.accept()
            rcvd_data = connection.recv(4096).decode("utf-8")
            if rcvd_data:
                socket_parser.rasp_parser(rcvd_data)




"""

Functions that is called by the Sending  thread, it as the objective to check for the status of the ip and send it periodicly

"""


def send_socket(message):
    sender_server = ('jdvalverde.dynip.sapo.pt', 4662)

    logging.info('Reaching %s on port %s' % sender_server)
    logging.info('Trying to send "%s"' % message)
    sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            sender_sock.connect(sender_server)

        except socket.error:
            logging.info("Cant connect at the time")
            time.sleep(10)
            continue
        else:
            logging.info("Connected to %s on port %s " % sender_server)
            break

    try:
        logging.info('Sending: "%s"' % message)
        sender_sock.sendall(str(message).encode('utf-8'))

        # TODO: check for successful delivery through this socket!

    finally:
        sender_sock.close()