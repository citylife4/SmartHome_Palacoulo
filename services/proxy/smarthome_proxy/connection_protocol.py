import logging


def h_noop(data, self):
    logging.error("Not Implemented Received: {}".format(data))


def h_webserver_trigger_ip(data, self):
    logging.info("Received h_trigger_ip: : {}".format(data))
    # TODO: Arduino connection
    # if ok
    self.send_message("received")
    return '_'.join(data)


def h_arduino_door_belt():
    # TODO
    pass
 

handlers = {
    "tr": h_webserver_trigger_ip,
    "dt": h_arduino_door_belt,
}


def parser(data, self):
    while len(data) >= 2:
        packet_id = data[0:2]
        if packet_id not in handlers:
            data = data[1:]
        else:
            data_list = list(filter(None, data[2:].split('_')))
            data = handlers.get(packet_id, h_noop)(data_list, self)
