class packet:
    def __init__(self, data: list[bytes] = [b'no data'], name: bytes = b"no name") -> None:
        self.data =  [len(name).to_bytes(1, "big"), name] + data
        self.name = name
        self.length = len(data)
