import socket


class EmpaticaClient:
    def __init__(self):
        self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_conn.connect(('127.0.0.1', 28000))

    def send(self):
        raise NotImplemented
