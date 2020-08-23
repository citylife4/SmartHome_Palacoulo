import time
import socket
import select
import logging
import miniupnpc

from requests import get
from threading import Thread
from .connection_protocol import parser
from Crypto.Util import Counter
from Crypto.Cipher import AES

import smarthome_relay.config as config

#TODO: Change bellow key and IV
key = b'Jimmy ffffffffff'
IV = b'1234567891234567'

#Global Logging
logger = logging.getLogger(__name__)

#TODO: Change this to be configurable
IPWAITTIME = 20

#Needed Global


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
    #logger.debug(s.getsockname()[0])
    # addportmapping(external-port, protocol, internal-host, internal-port, description, remote-host)
    try:
        return upnp.addportmapping(port_no, 'TCP', s.getsockname()[0], port_no, 'testing', '')
    except Exception as e:
        pass

# create the connection and check if something is getting through
class ServerThread(Thread):
    def __init__(self, host='', port=45321):
        super(ServerThread, self).__init__()
        logger.debug("[ServerThread] Starting")

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
        logger.info('[ServerThread] Sending: "%s"' % message)
        self.listening_socket.sendall(do_encrypt(message))

    def run(self):
        logger.info("[ServerThread] Running ")
        while 1:
            self.listening_socket, addr = self.connection_socket.accept()
            logger.info("[ServerThread] Acepted: "+ str(addr))
            while 1:
                try:
                    #Always pooling... maybe check this?
                    ready_to_read, ready_to_write, in_error = \
                        select.select([self.listening_socket,], [self.listening_socket,], [], 5)
                except select.error as e:
                    self.listening_socket.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                    self.listening_socket.close()
                    # connection error event here, maybe reconnect
                    logger.error( '[ServerThread] 0001 connection error, '+ str(e))
                    config.SERVER_CONNECTION = False
                    break

                if len(ready_to_read) > 0:
                    logger.info("[ServerThread] Waiting Data: ")
                    try:
                        rcvd_data = self.listening_socket.recv(2048)
                    except socket.error as e:
                        logger.error ( '[ServerThread] 0002 connection error, '+ str(e))
                        config.SERVER_CONNECTION = False
                        break
                    #TODO: had utf8 issues UnicodeDecodeError:
                    rcvd_data = do_decrypt(rcvd_data).decode()
                    #logger.info("[ServerThread] Received: " + rcvd_data)
                    if rcvd_data:
                        parser(rcvd_data, self)
                    else:
                        self.listening_socket.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                        self.listening_socket.close()
                        # connection error event here, maybe reconnect
                        logger.error( '[ServerThread] 0003 connection error, receiving empty')
                        config.SERVER_CONNECTION = False
                        break
            logger.info("[ServerThread] Exiting - Waiting Connection")
            self.listening_socket.close()
            


class ClientThread(Thread):
    def __init__(self, host="dvalverde.ddns.net", port=54897, relay_name="porto"):
        super(ClientThread, self).__init__()
        logger.debug("[ClientThread] Starting")
        self.packet_id = "ip"
        #TODO: Change to variable
        self.check_connection = "connect_"+relay_name
        self.my_address = ""
        self.host = host
        self.sender_server = (host, port)
        self.connection_issues = 1
        self.send_ip = 0

    def client_receive_port(self):
        while True:
            try:
                logger.debug("[ClientThread] Connecting to %s on port %s " % self.sender_server)

                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sender_sock.connect(self.sender_server)
                logger.debug("[ClientThread] Connected to %s on port %s " % self.sender_server)
                logger.debug("[ClientThread] Sending {}".format(self.check_connection ))
                sender_sock.sendall(do_encrypt(self.check_connection ))
                time.sleep(1)
                received_data = do_decrypt(sender_sock.recv(16)).decode()
                logger.debug("[ClientThread] Received: {}".format(received_data))
                assert ("server" in received_data)
                self.client_own_port = int(received_data.split('_')[1])
                config.SERVER_CONNECTION = True
                return 1
            except socket.error as e:
                self.connection_issues = 1
                logger.warning("[ClientThread] Cant connect at the time {}".format(e))
                time.sleep(100)
                continue
            except AssertionError as e:
                logger.error("[ClientThread] Connection problems: {}".format(e))
                time.sleep(500)
                continue
            finally:
                logger.debug("[ClientThread] Exiting")
                sender_sock.close()
                time.sleep(1)

    def client_server_connection(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.host, self.client_own_port))
        except socket.error as e:
                self.connection_issues = 1
                logger.warning("[ClientThread] client_server_connection: Cant connect at the time {}".format(e))
                time.sleep(1)
                return 0
        while True:
            if len(config.CLIENT_QUEUE)>0:
                pkt = config.CLIENT_QUEUE.pop()
                logger.debug("[ClientThread] Sending {}".format(pkt))
                #print "got queue client: {}".format(pkt.encode('hex'))
                self.server.sendall(do_encrypt(pkt))
                logger.debug("[ClientThread] Sent")
            elif not config.SERVER_CONNECTION:
                logger.warning("[ClientThread] client_server_connection: Returning")
                return 0




    def run(self):
        logger.info("[ClientThread] Running " + self.name)
        valid_port = False
        while 1:
            valid_port = self.client_receive_port()
            #TODO: check return
            if valid_port:
                time.sleep(1)
                valid_port = self.client_server_connection()
                logger.warning("[ClientThread] run: Returning")


