import time

def log(message: str):
    print(f"[{time.strftime('%X')}] {message}")

def error(message: str):
    print(f"[{time.strftime('%X')}] ERROR: {message}")

def warning(message: str):
    print(f"[{time.strftime('%X')}] WARNING: {message}")

def messageFromServer(message: str):
    print(f"[{time.strftime('%X')}] SERVER: {message}")

def messageFromClient(message: str):
    print(f"[{time.strftime('%X')}] CLIENT: {message}")
