import os
import socket

basedir = os.path.abspath(os.path.dirname(__file__))

HOUSEHOLDE_QUEUE = []
SERVER_QUEUE     = []

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

#FOR_RASP = True if "raspberry" in socket.gethostname() else False
FOR_RASP = False

DOOR_TIMEOUT = 20

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

if FOR_RASP:
   # interface = 'ppp0'
    interface = 'eth0'
else:
    interface = 'eth0'
    
