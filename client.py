import socket, time, console
from typing_extensions import Set
from threading import Thread
from packet import keepAlivePacket, configurationPacket, messagePacket, packet
HOST = 'localhost'
PORT = 5001

KEEP_ALIVE_INTERVAL = 3

def stableConnection():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        def sendPacket(packet: packet):
            time.sleep(.01) # technically slowing down but its fine + necessary
            try:
                test = b''
                for b in packet.data:
                    test += b
                data = bytearray(test)
                s.sendall(data)
            except BrokenPipeError:
                console.error("error sending packet: broken pipe/connection lost (server down?)")
                s.close()
                raise SystemExit # closes the thread

        def heartbeat():
            time.sleep(KEEP_ALIVE_INTERVAL)
            sendPacket(keepAlivePacket())
            #console.log("sent keepAlive packet")
            heartbeat()

        sendPacket(configurationPacket("client", "Client"))
        heartbeatDaemon = Thread(target=heartbeat)
        heartbeatDaemon.daemon = True
        heartbeatDaemon.start()

        while True:
            data = s.recv(1024)
            if not data:
                break

            # PACKING HANDLING
            packetName = data[1:data[0]+1]
            packetData = data[data[0]+1:]

            if(packetName == b"message"):
                # message packet from client - message
                message = packetData[1:packetData[0]+1].decode('utf-8')
                console.messageFromServer(message)
            else:
                console.log(f'received unknown data from server: {repr(data)}')

connectionDaemon = Thread(target=stableConnection)
connectionDaemon.daemon = True
connectionDaemon.start()

console.log(f"connected to server - {HOST}")

while True:
    if(not connectionDaemon.is_alive()): # connection daemon died
        console.error("connection lost")
        raise ConnectionError("connection to server lost")
    time.sleep(.1) # idling
