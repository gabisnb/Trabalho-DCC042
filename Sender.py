import socket
import time
import random
import asyncio

from UDPSecure import UDPSecure



#? --------------Sender Class--------------
class Sender(UDPSecure):
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
        data, address, pktSize = super().receive()
        messages = data.decode().split(",")
        if messages[0] == "SYN-ACK":
            self.sequenceSize = int(messages[1])
            self.windowSize = int(messages[2])
            self.windowStart = 0
            self.rcvIp = ip
            self.rcvPort = port
            super().send(ip, port, b"ACK")
            print("números de sequencia:" + str(self.sequenceSize))

    def disconnect(self):
        super().send(self.rcvIp, self.rcvPort, b"FIN")
        data, address, pktSize = super().receive()
        if data.decode() == "FIN-ACK":
            super().send(self.rcvIp, self.rcvPort, b"ACK")

    def send(self, ip, port, data):
        data = (str(self.currentIndex) + ":").encode() + data
        if self.currentIndex == self.windowStart:
            self.timer = time.time()
        super().send(ip, port, data)
        self.timer = time.time()
        error = self.waitAck()
        if error:
            return
        self.currentIndex = (self.currentIndex + len(data)) % self.sequenceSize

    def waitAck(self):
        while time.time() - self.timer < self.maxTimer:
            data, address, pktSize = super().receive()
            metadata = self.extractMetadata(data)
            if metadata[0] == "Erro" or len(metadata)!=2:
                print(data.decode())
                return True
            nextPkt = metadata[0]
            availableBuff = metadata[1]
            sequenceNum = int(nextPkt)
            if sequenceNum != self.windowStart:
                self.timer = time.time()
            print(self.markPkt(sequenceNum))
            return False
        return True

    def markPkt(self, index):
        # if self.isNotInWindow(index):
        #     return "Erro: Pacote fora da janela " + str(self.windowStart) + " a " + str((self.windowStart + self.windowSize-1)%self.sequenceSize)
        previousStart = self.windowStart
        self.windowStart = index
        self.updateTimer()
        return str(previousStart) + " a " + str(index-1%self.sequenceSize) + ": Recebido!"
    
    def __del__(self):
        self.disconnect()
        super().__del__()
