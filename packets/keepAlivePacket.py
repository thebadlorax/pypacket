from .packet import packet

class keepAlivePacket(packet):
    def __init__(self) -> None:
        super().__init__(
            [b'keepAlive'],
            b"keepAlive")
