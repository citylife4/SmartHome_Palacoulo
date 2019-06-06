import socket
import time
import logging

from threading import Thread

from requests import get

from connection_protocol import parser

IPWAITTIME = 10


# create the connection and check if something is getting through
class ServerThread(Thread):
    def __init__(self, host='', port=45321):
        super(ServerThread, self).__init__()

        self.address = (host, port)
        self.listening_socket = None

        self.connection_socket = socket.socket(
            socket.AF_INET
            , socket.SOCK_STREAM
        )
        self.connection_socket.setsockopt(
            socket.SOL_SOCKET
            , socket.SO_REUSEADDR
            , 1
        )
        self.connection_socket.bind(self.address)
        self.connection_socket.listen(1)

    def send_message(self, message):
        logging.info('ReceiverThread: "%s"' % message)
        self.listening_socket.sendall(message.encode('utf-8'))

    def run(self):
        logging.info("ReceiveThread Thread - Starting ")
        while 1:
            self.listening_socket, addr = self.connection_socket.accept()
            rcvd_data = self.listening_socket.recv(4096).decode("utf-8")
            logging.info("ReceiveThread - Acepted: " + rcvd_data)
            if rcvd_data:
                parser(rcvd_data, self)
            logging.info("ReceiveThread Thread - Exiting")


class ClientThread(Thread):
    def __init__(self, host="jdvalverde.dynip.sapo.pt", port=4662):
        super(ClientThread, self).__init__()
        self.packet_id = "ip"
        self.check_connection = "ch_palacoulo"
        self.my_address = ""
        self.sender_server = (host, port)
        self.connection_issues = 1

    def send_to_host(self, message):
        while True:
            try:
                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sender_sock.connect(self.sender_server)
                logging.debug("Connected to %s on port %s " % self.sender_server)
                logging.debug("Sending {}".format(message))
                sender_sock.sendall(str(message).encode('utf-8'))
                received_data = sender_sock.recv(16).decode()
                assert ("porto" in received_data)
                logging.debug("Received: {}".format(received_data))
                break
            except socket.error as e:
                self.connection_issues = 1
                logging.error("Cant connect at the time {}".format(e))
                time.sleep(10)
                continue
            except AssertionError as e:
                logging.error("Connection problems: {}".format(e))
                time.sleep(10)
                continue
            finally:
                logging.debug("Exiting")
                sender_sock.close()
                time.sleep(1)

    def run(self):
        logging.info("Starting " + self.name)
        while 1:
            new_address = get('https://ipapi.co/ip/').text
            self.send_to_host(self.check_connection)
            logging.debug("my address {}".format(self.my_address))
            logging.debug("new address {}".format(new_address))
            if self.my_address not in new_address or self.connection_issues:
                self.connection_issues = 0
                self.my_address = new_address
                to_send = "{}_{}".format(self.packet_id, new_address)
                self.send_to_host(to_send)
            time.sleep(IPWAITTIME)
