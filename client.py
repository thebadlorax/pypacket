import time

from connections.ServerConnection import ServerConnection

# SERVER CONFIG
HOST = 'localhost'
PORT = 5001

# CLIENT CONFIG
USERNAME = "client"
DISPLAYNAME = "Client"

connection = ServerConnection(HOST, PORT, USERNAME, DISPLAYNAME)

while True:
    # actual game goes here
    time.sleep(.1)
