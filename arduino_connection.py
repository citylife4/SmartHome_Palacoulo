import logging
from threading import Thread

class HouseholdConnection(Thread):
    def __init__(self):
        super(HouseholdConnection, self).__init__()
        """
        self.arduino_ser = serial.Serial('/dev/serial0',
                                         baudrate=4800,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS,
                                         timeout=1)
        """

    def run(self):
        logging.info("Starting Arduino Connection")
        """
        while 1:
            time.sleep(0.01)
            while self.arduino_ser.in_waiting:
                arduino_parser(self.arduino_ser.readline.decode("utf-8"))
        """

    def send_message(message):
        print(message)

    def set(self, value):
        self.pong = value
