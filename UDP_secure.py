import socket

__all__ = ['UDP_buffed']

class UDP_secure:
    def __init__(self, ip, port, buff):
        self.ip = ip
        self.port = port
        self.buffer = buff
        self.protocol = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.socket.sendto(data, (self.ip, self.port))
    
    def receive(self, from_ip):
        self.socket.bind((from_ip, self.port))
        while True:
            data, address = self.socket.recvfrom(self.buffer)
            print("Received:", data, "from", address)

    def __del__(self):
        self.socket.close()