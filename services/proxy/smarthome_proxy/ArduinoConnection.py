import os
import logging
import serial
import serial.tools.list_ports
import warnings
import socket
import json
from threading import Thread
from enum import Enum

from datetime import datetime



import smarthome_proxy.config as config

class CommandType(Enum):
    """ Received Command """

    SET       = 0
    GET       = 1
    CONFIG    = 2
    MEM_DEBUG = 3
    Unknown   = -1

class HouseholdConnection(Thread):
    def __init__(self):
        super(HouseholdConnection, self).__init__()
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # may need tweaking to match new arduinos
        ]
        if not arduino_ports:
            ## TODO: check if not Debug/ CICD Mode
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
        while True:
            serial.time.sleep(0.01)
            while self.arduino_ser.in_waiting:
                data = self.arduino_ser.readline().decode("utf-8")
                try:
                    self.decode(data)
                    if len(config.HOUSEHOLDE_QUEUE)>0:
                        pkg = config.HOUSEHOLDE_QUEUE.pop()
                        self.write(pkg)
                    pass
                except Exception as e:
                    print ('HouseHoulde: ', e)

    def write(self,message):
        self.arduino_ser.write(message)

    def send_message(self, message):
        print(message)

    def set(self, value):
        self.pong = value

    def create_decoded_json(self, data_list, print_json=True):
        """ Should datalist be already parsed? """

        print(data_list)
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")

        #TODO error detection
        decoded_json = {
            "data" : current_time,
            "from" : data_list[0],
            "to" : data_list[1],
            "command" : CommandType(data_list[2]).name,
            "GPIO" : data_list[3],
            "value" : data_list[4]
        }

        if print_json ==True :
            self.write_json(decoded_json)

        return decoded_json

    def write_json(self, data, filename=config.basedir+'/../json_data/data.json'): 
        with open(filename) as f: 
            try:
                json_file = json.load(f)
            except Exception as e:
                print("Exception: ", e)
                json_file = { 'GPIOS' : []}
            json_file['GPIOS'].append(data)
        with open(filename, 'w') as f: 
            json.dump(json_file, f) 

    #from_to_command_gpio_value
    def decode(self, data):

        #gpios = {
        #    "13": self.h_door_state,
        #}
        try:
            data_list = list(filter(None, data.rstrip().split('_')))
            data_list = [int(i) for i in data_list]
            json = self.create_decoded_json(data_list)
            config.SERVER_QUEUE.append(json)
        except Exception as e:
            print(e)



