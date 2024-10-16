from os import remove
import socket, time
from threading import Thread

from packets.keepAlivePacket import keepAlivePacket
from packets.configurationPacket import configurationPacket
from packets.messagePacket import messagePacket
from packets.disconnectPacket import disconnectPacket
from packets.packet import packet

from console import Console


# SERVER CONFIG
HOST = 'localhost'
PORT = 5001
DISCONNECTION_TIME = 5

# VARIABLES
CONNECTIONS = []
DEAD_CONNECTIONS = []
console = Console()

def checkIfAlive():
    for i in CONNECTIONS:
        if(time.time() - i[2] > DISCONNECTION_TIME):
            console.warning(f"connection abruptly lost with client: {i[1][0]}")
            i[0].close()
            DEAD_CONNECTIONS.append(i)
            CONNECTIONS.remove(i)
    time.sleep(1)
    checkIfAlive()

aliveDaemon = Thread(target=checkIfAlive)
aliveDaemon.daemon = True
aliveDaemon.start()

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        console.log(f"server started on {HOST}:{PORT}")
        s.listen()
        conn, addr = s.accept()
        isDead = False
        username = None
        displayname = None
        for i in DEAD_CONNECTIONS:
            if(i[1][0] == addr[0]):
                username = i[3]
                displayname = i[4]
                DEAD_CONNECTIONS.remove(i)
                isDead = True
        CONNECTIONS.append([conn, addr, time.time(), username, displayname])

        with conn:
            def sendPacket(packet: packet):
                time.sleep(.01) # technically slowing down but its fine + necessary
                test = b''
                for b in packet.data:
                    test += b
                data = bytearray(test)
                conn.sendall(data)

            if not isDead:
                console.log(f'new connection: {addr[0]}')
                sendPacket(messagePacket("first connection"))
            else:
                console.log(f"reviving dead client: {addr[0]}")
                for i in CONNECTIONS:
                    if(i[0] == conn):
                        sendPacket(messagePacket(f"welcome back, {i[4]}"))
                isDead = False

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                # PACKING HANDLING
                packetName = data[1:data[0]+1]
                packetData = data[data[0]+1:]

                if(packetName == b"keepAlive"):
                    # keepAlive from client
                    for i in CONNECTIONS:
                        if(i[0] == conn):
                            i[2] = time.time()

                elif(packetName == b"configuration"):
                    # configuration packet from client - username and displayname
                    for i in CONNECTIONS:
                        if(i[0] == conn):
                            if i[3] is not None:
                                console.log("configuration packet ignored: already restored")
                            else:
                                console.log("configuration packet recieved")
                                username = packetData[1:packetData[0]+1].decode('utf-8')
                                displayname = packetData[packetData[0]+2:].decode('utf-8')
                                #console.log(f"username: {username}, displayname: {displayname}")
                                i[3] = username
                                i[4] = displayname
                                sendPacket(messagePacket(f"configuration accepted, {i[4]}"))

                elif(packetName == b"message"):
                    # message packet from client - message
                    message = packetData[1:packetData[0]+1].decode('utf-8')
                    console.messageFromClient(message)

                elif(packetName == b"disconnect"):
                    for i in CONNECTIONS:
                        if(i[0] == conn):
                            console.log(f"{i[4]} is disconnecting")
                            sendPacket(messagePacket(f"byebye"))
                            DEAD_CONNECTIONS.append(i)
                            CONNECTIONS.remove(i)

                else:
                    console.log(f'received unknown data from {addr[0]}: {repr(data)}')
