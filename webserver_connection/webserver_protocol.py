
import struct
import logging
from sqlite3 import DatabaseError


def h_noop(data):
    logging.error("Not Implemented Received: {}".format(data))


def h_trigger_ip(data):
    logging.info("Received h_trigger_ip: " + data)

    return '_'.join(data)


handlers = {
    "tr" : h_trigger_ip,

}


def webserver_parser(data):
    while len(data)>=2:
        packet_id = data[0:2]
        if packet_id not in handlers:
            data = data[1:]
        else:
            data_list = list(filter(None,data[2:].split('_')))
            data = handlers.get(packet_id, h_noop)(data_list)