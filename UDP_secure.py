import socket
import time

__all__ = ['UDP_buffed']

class UDP_secure:
    def __init__(self, ip, port, buff):
        self.ip = ip
        self.port = port
        self.buffer = buff
        self.protocol = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timer = None
        self.maxTimer = 100

    def send(self, ip, port, data):
        self.socket.sendto(data, (ip, port))
        if(self.timer == None):
            self.timer = time.time()
    
    def receive(self, from_ip):
        self.socket.bind((from_ip, self.port))
        while True:
            data, address = self.socket.recvfrom(self.buffer)
            print("Received:", data, "from", address)
            self.send(address[0], address[1], b"Recebido!")

    def waitAck(self):
        while time.time() - self.timer < self.maxTimer:
            data, address = self.socket.recvfrom(self.port)
            print("Received:", data, "from", address, "in", time.time() - self.timer)
            break

    def __del__(self):
        self.socket.close()