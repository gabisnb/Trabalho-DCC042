import socket
import time
import random

from UDP_secure import UDP_secure



#? --------------Server Class--------------
class Server(UDP_secure):
    def __init__(self, ip, port, buff, wndSize=8):
        super().__init__(ip, port, buff)
        self.windowSize = wndSize
        self.sequenceSize = self.windowSize * 2 + 1
        self.windowStart = 0
        self.window = []
        for i in range(self.sequenceSize):
            self.window.append(False)

    def waitConnection(self):
        data, address = super().receive()
        message = data.decode()
        if message == "SYN":
            super().send(address[0], address[1], ("SYN-ACK,"  + str(self.sequenceSize) + "," + str(self.windowSize)).encode())
            data, address = super().receive()
            if data.decode() == "ACK":
                self.sdnIp = address[0]
                self.sdnPort = address[1]
            else:
                print("Erro: Resposta inesperada")
        else:
            print("Erro: Resposta inesperada")

    def disconnect(self, address):
        super().send(address[0], address[1], b"FIN-ACK")
        self.sdnIp = None
        self.sdnPort = None
        data, address = super().receive()
        if data.decode() == "ACK":
            return
    
    def receive(self):
        while True:
            data, address = super().receive()
            # if random.randint(0, 1) >= 0.2:
            if data.decode() == "FIN":
                self.disconnect(address)
                return
            sequenceNum = int((data.decode()).split(":")[0])
            ack = self.markPkt(sequenceNum)
            self.send(address[0], address[1], (ack).encode())

    def markPkt(self, index):
        if self.isNotInWindow(index):
            if self.window[index]:
                return str(index) + ": Recebido!"
            return "Erro: Pacote fora da janela " + str(self.windowStart) + " a " + str((self.windowStart + self.windowSize-1)%self.sequenceSize)
        self.window[index] = True
        self.moveWindow()
        return str((self.windowStart-1)%self.sequenceSize) + ": Recebido!"

    def moveWindow(self):
        i = self.windowStart

        # Move início da janela até primeiro pacote não confirmado
        while self.window[i]:
            # self.window[i] = False
            self.window[(i+self.windowSize)%self.sequenceSize] = False
            i = (i+1)%self.sequenceSize # Garante que i será um nº de sequência válido
        self.windowStart = i
