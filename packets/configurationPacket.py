from .packet import packet

class configurationPacket(packet):
    def __init__(self, userName: str, displayName: str) -> None:
        super().__init__(
            [len(userName).to_bytes(1, "big"), userName.encode('utf-8'),
            len(displayName).to_bytes(1, "big"), displayName.encode('utf-8')],
            b"configuration")
