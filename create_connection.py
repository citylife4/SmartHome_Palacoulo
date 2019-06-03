import time
import socket

from requests import get

my_address = get('https://api.ipify.org').text

sender_server = ('jdvalverde.dynip.sapo.pt', 4662)
print ('starting up on %s port %s' % sender_server)
sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_sock.connect(sender_server)
sender_sock.sendall('ola')


while 1:

    new_address = get('https://api.ipify.org').text
    if my_address is not new_address:
        my_address = new_address
        sender_sock.sendall('ola')

    time.sleep(600)

