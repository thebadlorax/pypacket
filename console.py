import time, os

class Console:
    def __init__(self) -> None:
        self.messageLimit = 25
        self.messages = []
        self.free = True

    def getPrefix(self) -> str:
        return f"[{time.strftime('%X')}]"

    def addMessage(self, message: str, extra: str = "") -> None:
        msg = f"{self.getPrefix()}{extra}: {message}"
        print(len(self.messages))

        if(len(self.messages) >= self.messageLimit): self.messages.pop(0) # remove oldest message
        self.messages.append(msg)

        self.refresh()

    def log(self, message: str) -> None:
        self.addMessage(message)

    def error(self, message: str) -> None:
        self.addMessage(message, " ERROR")

    def warning(self, message: str) -> None:
        self.addMessage(message, " WARNING")

    def messageFromServer(self, message: str) -> None:
        self.addMessage(message, " SERVER")

    def messageFromClient(self, message: str) -> None:
        self.addMessage(message, " CLIENT")

    def printMessages(self) -> None:
        for m in self.messages:
            print(m)

    def clear(self) -> None:
        os.system("clear")

    def refresh(self) -> None:
        self.clear()
        self.printMessages()
