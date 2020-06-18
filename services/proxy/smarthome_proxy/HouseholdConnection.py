import logging
import serial
import serial.tools.list_ports
import warnings
import socket
from threading import Thread
import ServerConnection

class HouseholdConnection(Thread):
    def __init__(self):
        super(HouseholdConnection, self).__init__()
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # may need tweaking to match new arduinos
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            warnings.warn('Multiple Arduinos found - using the first')

        self.arduino_ser = serial.Serial(arduino_ports[0],
                                    baudrate=9600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=1)

    def run(self):
        logging.info("Starting Arduino Connection")
        while 1:
            serial.time.sleep(0.01)
            while self.arduino_ser.in_waiting:
                self.decode(self.arduino_ser.readline().decode("utf-8"))

    def write(self,message):
        self.arduino_ser.write(message)

    def send_message(message):
        print(message)

    def set(self, value):
        self.pong = value

    #from_to_command_gpio_value
    def decode(self, data):

        #gpios = {
        #    "13": self.h_door_state,
        #}
        data_list = list(filter(None, data.rstrip().split('_')))
        data_list = [int(i) for i in data_list]

        #Todo Change this a suttlibe function
        if not data_list[1]:
            if data_list[3] == 13:
                if data_list[2]:
                    message = "st_"+str(data_list[4])
                    logging.debug("Sending {}".format(message))
                    try: 
                        self.sender_server = ("dvporto.dynip.sapo.pt", 4662)
                        sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sender_sock.connect(self.sender_server)
                        logging.debug("Connected to %s on port %s " % self.sender_server)
                        sender_sock.sendall(str(message).encode('utf-8'))
                    except ConnectionRefusedError:
                        logging.debug("conection failed")
                        

