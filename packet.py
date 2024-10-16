class packet:
    def __init__(self, data: list[bytes] = [b'no data'], name: bytes = b"no name"):
        self.data =  [len(name).to_bytes(1, "big"), name] + data
        self.name = name
        self.length = len(data)

# PACKETS
class keepAlivePacket(packet):
    def __init__(self):
        super().__init__([b'keepAlive'], b"keepAlive")

class configurationPacket(packet):
    def __init__(self, userName: str, displayName: str):
        super().__init__(
            [len(userName).to_bytes(1, "big"), userName.encode('utf-8'),
                len(displayName).to_bytes(1, "big"), displayName.encode('utf-8')],
            b"configuration")

class messagePacket(packet):
    def __init__(self, message: str):
        super().__init__(
            [len(message).to_bytes(1, "big"), message.encode('utf-8')],
            b"message")
