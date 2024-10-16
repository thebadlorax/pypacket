from .packet import packet

class disconnectPacket(packet):
    def __init__(self) -> None:
        super().__init__(
            [b"disconnect"],
            b"disconnect")
