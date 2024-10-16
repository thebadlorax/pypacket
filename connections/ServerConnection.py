import socket, time
from threading import Thread
from typing_extensions import Callable

from packets.keepAlivePacket import keepAlivePacket
from packets.configurationPacket import configurationPacket
from packets.messagePacket import messagePacket
from packets.disconnectPacket import disconnectPacket
from packets.packet import packet

from console import Console

console = Console()

def configureDaemon(target: Callable) -> Thread:
    daemon = Thread(target=target)
    daemon.daemon = True
    return daemon

class ServerConnection():
    def __init__(self, host: str, port: int, username: str = "null", displayname: str = "null") -> None:
        # general variables
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PACKETS_TO_SEND = []
        self.KEEP_ALIVE_INTERVAL = 3
        self.INTENSIVE_LOGGING = True

        # configs
        self.host = host
        self.port = port
        self.username = username
        self.displayname = displayname

        # Daemons - these get modified during init process
        self.connectionDaemon: Thread = Thread()
        self.sendOutgoingPacketsDaemon: Thread = Thread()
        self.handleIncomingPacketsDaemon: Thread = Thread()
        self.heartbeatDaemon: Thread = Thread()

        def run() -> None:
            try:
                self.socket.connect((host, port))
            except ConnectionRefusedError:
                console.error("error connecting to server: connection refused")
                raise SystemExit

            console.log(f"connected to server - {self.host}")

            def heartbeat() -> None:
                time.sleep(self.KEEP_ALIVE_INTERVAL)
                self.addPacketToQueue(keepAlivePacket())
                if(self.INTENSIVE_LOGGING): console.log("sent keep alive packet")
                heartbeat()

            def sendOutgoingPackets() -> None:
                while True:
                    for p in self.PACKETS_TO_SEND:
                        if(issubclass(p.__class__, packet)):
                            self.sendPacket(p)
                            self.PACKETS_TO_SEND.remove(p)

            def handleIncomingPackets() -> None:
                while True:
                    data = self.socket.recv(1024)
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

            self.sendPacket(configurationPacket(self.username, self.displayname))

            self.sendOutgoingPacketsDaemon = configureDaemon(sendOutgoingPackets)
            self.sendOutgoingPacketsDaemon.start()

            self.heartbeatDaemon = configureDaemon(heartbeat)
            self.heartbeatDaemon.start()

            self.handleIncomingPacketsDaemon = configureDaemon(handleIncomingPackets)
            self.handleIncomingPacketsDaemon.start()

            while True:
                if(not self.isAlive()): # connection daemon died
                    console.error("connection lost")
                    raise ConnectionError("connection to server lost")

        self.connectionDaemon = configureDaemon(run)
        self.connectionDaemon.start()

    def sendPacket(self, packet: packet) -> None:
        time.sleep(.01) # technically slowing down but its fine + necessary
        try:
            test = b''                # transform list[bytes] to one big string and shove it into a bytearray
            for b in packet.data:     #
                test += b             #
            data = bytearray(test)    #
            self.socket.sendall(data) # send the bytearray
        except BrokenPipeError:
            console.error("error sending packet: broken pipe/connection lost (server down?)")
            self.socket.close()
            raise SystemExit # closes the thread

    def addPacketToQueue(self, packet: packet) -> None:
        self.PACKETS_TO_SEND.append(packet)

    def isAlive(self) -> bool:
        return self.connectionDaemon.is_alive()
