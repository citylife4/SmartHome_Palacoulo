import logging
import struct
import time

SERVER_QUEUE = []
CLIENT_QUEUE = []

# For now Porto arduino is kinda simple
def h_noop(data):
    return data


#handlers = {
#    "manualy"  : h_door_belt,
#    "remotaly" : h_remote_belt
#}


def arduino_parser(data):
    if "opening" in data:
        insert_porto_door(data)
    logging.info("arduino_parser - received:" + data)