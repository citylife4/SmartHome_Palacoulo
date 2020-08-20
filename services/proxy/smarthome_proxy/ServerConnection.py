import socket
import time
import logging
import select

from threading import Thread

from requests import get
import miniupnpc

from .connection_protocol import parser

IPWAITTIME = 20
from Crypto.Cipher import AES
from Crypto.Util import Counter

key = b'Jimmy ffffffffff'
IV = b'1234567891234567'

def do_encrypt(message):
    iv_int = int.from_bytes(IV, byteorder='big')

    new_counter = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=new_counter)
    return cipher.encrypt(message)

def do_decrypt(message):
    iv_int = int.from_bytes(IV, byteorder='big')
    new_counter = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=new_counter)
    return cipher.decrypt(message)


def open_port(port_no):
    '''this function opens a port using upnp'''
    upnp = miniupnpc.UPnP()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))

    upnp.discoverdelay = 10
    upnp.discover()

    upnp.selectigd()
    #print(s.getsockname()[0])
    # addportmapping(external-port, protocol, internal-host, internal-port, description, remote-host)
    try:
        return upnp.addportmapping(port_no, 'TCP', s.getsockname()[0], port_no, 'testing', '')

    except Exception as e:
        pass

# create the connection and check if something is getting through
class ServerThread(Thread):
    def __init__(self, host='', port=45321):
        super(ServerThread, self).__init__()
        logging.debug("[ServerThread] Starting")

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
        open_port(port)
        self.connection_socket.bind(self.address)
        self.connection_socket.listen(1)

    def send_message(self, message):
        logging.info('[ServerThread] Sending: "%s"' % message)
        self.listening_socket.sendall(do_encrypt(message))

    def run(self):
        logging.info("[ServerThread] Running ")
        while 1:
            self.listening_socket, addr = self.connection_socket.accept()
            logging.info("[ServerThread] Acepted: "+ str(addr))
            while 1:
                try:
                    #Always pooling... maybe check this?
                    ready_to_read, ready_to_write, in_error = \
                        select.select([self.listening_socket,], [self.listening_socket,], [], 5)
                except select.error as e:
                    self.listening_socket.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                    self.listening_socket.close()
                    # connection error event here, maybe reconnect
                    print( '[ServerThread] connection error, ', e)
                    break

                if len(ready_to_read) > 0:
                    #logging.info("[ServerThread] Waiting Data: ")
                    try:
                        rcvd_data = self.listening_socket.recv(2048)
                    except socket.error as e:
                        print ( '[ServerThread] connection error, ', e)
                        break
                    rcvd_data = do_decrypt(rcvd_data).decode()
                    #logging.info("[ServerThread] Received: " + rcvd_data)
                    if rcvd_data:
                        parser(rcvd_data, self)
                    if not rcvd_data:
                        self.listening_socket.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                        self.listening_socket.close()
                        # connection error event here, maybe reconnect
                        print( '[ServerThread] connection error')
                        break
            logging.info("[ServerThread] Exiting - Waiting Connection")
            self.listening_socket.close()
            


class ClientThread(Thread):
    def __init__(self, host="dvalverde.ddns.net", port=54897):
        super(ClientThread, self).__init__()
        logging.debug("[ClientThread] Starting")
        self.packet_id = "ip"
        self.check_connection = "ch_palacoulo"
        self.my_address = ""
        self.sender_server = (host, port)
        self.connection_issues = 1
        self.send_ip = 0

    def send_to_host(self, message):
        while True:
            try:
                logging.debug("[ClientThread] Connected to %s on port %s " % self.sender_server)

                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sender_sock.connect(self.sender_server)
                logging.debug("[ClientThread] Connected to %s on port %s " % self.sender_server)
                logging.debug("[ClientThread] Sending {}".format(message))
                sender_sock.sendall(do_encrypt(str(message)))
                time.sleep(1)
                logging.debug("[ClientThread] bla")
                received_data = do_decrypt(sender_sock.recv(16)).decode()
                logging.debug("[ClientThread] Received: {}".format(received_data))
                #assert ("porto" in received_data)
                break
            except socket.error as e:
                self.connection_issues = 1
                logging.error("[ClientThread] Cant connect at the time {}".format(e))
                time.sleep(10)
                continue
            except AssertionError as e:
                logging.error("[ClientThread] Connection problems: {}".format(e))
                time.sleep(10)
                continue
            finally:
                logging.debug("[ClientThread] Exiting")
                sender_sock.close()
                time.sleep(1)

    def run(self):
        logging.info("[ClientThread] Running " + self.name)
        while 1:
            new_address = "get('https://ipapi.co/ip/').text"
            self.send_to_host(self.check_connection)
            logging.debug("[ClientThread] my address {}".format(self.my_address))
            logging.debug("[ClientThread] new address {}".format(new_address))
            if self.my_address not in new_address or self.connection_issues:
                self.connection_issues = 0
                self.my_address = new_address
                to_send = "{}_{}".format(self.packet_id, new_address)
                self.send_to_host(to_send)
            time.sleep(IPWAITTIME)

