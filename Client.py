import socket
import time
import random

from UDP_secure import UDP_secure



#? --------------Client Class--------------
class Client(UDP_secure):
    def __init__(self, ip, port, buff):
        super().__init__(ip, port, buff)
        self.windowSize = 0
        self.sequenceSize = 0
        self.windowStart = 0
        self.timer = None
        self.maxTimer = 1
        self.currentIndex = 0

    def connect(self, ip, port):
        super().send(ip, port, b"SYN")
        data, address = super().receive()
        messages = data.decode().split(",")
        if messages[0] == "SYN-ACK":
            self.sequenceSize = int(messages[1])
            self.windowSize = int(messages[2])
            self.windowStart = 0
            self.rcvIp = ip
            self.rcvPort = port
            super().send(ip, port, b"ACK")

    def disconnect(self):
        super().send(self.rcvIp, self.rcvPort, b"FIN")
        data, address = super().receive()
        if data.decode() == "FIN-ACK":
            super().send(self.rcvIp, self.rcvPort, b"ACK")
        self.__del__()

    def send(self, ip, port, data):
        data = (str(self.currentIndex) + ":").encode() + data
        super().send(ip, port, data)
        # if self.timer == None:
        self.timer = time.time()
        error = self.waitAck()
        if error:
            return
        self.currentIndex = (self.currentIndex + 1) % self.sequenceSize

    def waitAck(self):
        while time.time() - self.timer < self.maxTimer:
            data, address = super().receive()
            message = (data.decode()).split(":")[0]
            if message == "Erro":
                print(data.decode())
                return True
            sequenceNum = int(message)
            if sequenceNum == self.windowStart:
                self.timer = time.time()
            self.markPkt(sequenceNum)
            return False
        return True

    def markPkt(self, index):
        if self.isNotInWindow(index):
            return "Erro: Pacote fora da janela " + str(self.windowStart) + " a " + str((self.windowStart + self.windowSize-1)%self.sequenceSize)
        self.moveWindow(index)
        return str(index) + ": Recebido!"

    def moveWindow(self, index):
        self.windowStart = (index + 1) % self.sequenceSize
