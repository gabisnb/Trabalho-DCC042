import socket
import time
import random

from UDPSecure import UDPSecure



#? --------------Server Class--------------
class Receiver(UDPSecure):
    def __init__(self, ip, port, buff):
        super().__init__(ip, port, buff)
        self.availableBuff = buff
        self.windowSize = self.availableBuff
        self.sequenceSize = self.windowSize * 2 + 1
        self.windowStart = 0
        self.window = []
        for i in range(self.sequenceSize):
            self.window.append(False)

    def waitConnection(self):
        data, address, pktSize = super().receive()
        message = data.decode()
        if message == "SYN":
            super().send(address[0], address[1], ("SYN-ACK,"  + str(self.sequenceSize) + "," + str(self.windowSize)).encode())
            data, address, pktSize = super().receive()
            if data.decode() == "ACK":
                self.sdnIp = address[0]
                self.sdnPort = address[1]
            else:
                print("Erro: Resposta inesperada")
        else:
            print("Erro: Resposta inesperada")

    def disconnect(self, address):
        try:
            super().send(address[0], address[1], b"FIN-ACK")
            self.sdnIp = None
            self.sdnPort = None
            data, address, pktSize = super().receive()
            self.updateTimer()
            while time.time() - self.timer < self.maxTimer:
                data, address, pktSize = super().receive()
                if data.decode() == "ACK":
                    break
            self.__del__()
        except Exception as e:
            print(Exception)
            self.__del__()
    
    def receive(self):
        while True:
            data, address, pktSize = super().receive()

            if data.decode() == "FIN":
                self.disconnect(address)

            sequenceNum = int(self.extractMetadata(data)[0])

            # Simulação de perda de pacotes (15% de perda, por exemplo)
            # if random.random() < 0.15:
            #     print(f"Pacote {sequenceNum} perdido!")
            #     continue  # Pacote descartado, não envia ACK

            ack = self.markPkt(sequenceNum, pktSize)
            self.send(address[0], address[1], ack.encode())
    def markPkt(self, index, pktSize):
        if self.isNotInWindow(index):
            if self.window[index]:
                return str(index) + ": Recebido!"
            return "Erro: Pacote fora da janela " + str(self.windowStart) + " a " + str((self.windowStart + self.windowSize-1)%self.sequenceSize)
        for i in range(pktSize):
            self.window[(index + i)%self.sequenceSize] = True
        self.availableBuff = self.availableBuff - pktSize
        self.moveWindow()
        nextPkt = str(index+pktSize%self.sequenceSize)
        ack = nextPkt + "," + str(self.availableBuff) + ": Recebido!"
        return ack
    
    def moveWindow(self):
        i = self.windowStart

        # Move início da janela até primeiro pacote não confirmado
        while self.window[i]:
            # self.window[i] = False
            self.window[(i+self.windowSize)%self.sequenceSize] = False
            self.availableBuff = self.availableBuff + 1
            i = (i+1)%self.sequenceSize # Garante que i será um nº de sequência válido
        self.windowStart = i
