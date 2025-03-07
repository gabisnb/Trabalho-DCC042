import socket
import time
import random

__all__ = ['UDP_buffed']

class UDP_secure:
    def __init__(self, ip, port, buff):
        self.ip = ip
        self.port = port
        self.buffer = buff
        self.protocol = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))

    def send(self, ip, port, data):
        self.socket.sendto(data, (ip, port))
        print("Enviou '" + data.decode() + "' com sucesso")

    def receive(self):
        data, address = self.socket.recvfrom(self.buffer)
        print("Recebeu:", data, "de", address)
        return data, address

    def isNotInWindow(self, index):
        wndSize = self.windowSize   # get window size
        wndStart = self.windowStart   # get window start
        wndEnd = (wndStart + wndSize)%self.sequenceSize   # calculate window end

        afterWndStart  = wndEnd > wndStart and (index >= wndEnd or  index < wndStart)  # index is after the window end and window end is not at the beginning of the sequence
        beforeWndStart = wndEnd < wndStart and (index >= wndEnd and index < wndStart)  # index is before the window start and window end is at the beginning of the sequence

        # if index is after the window end and window end is not at the beginning of the sequence or
        # if index is before the window start and window end is at the beginning of the sequence, 
        #     return True
        return afterWndStart or beforeWndStart

    def __del__(self):
        self.socket.close()

class Client(UDP_secure):
    def __init__(self, ip, port, buff, wndSize= 8):
        super().__init__(ip, port, buff)
        self.windowSize = wndSize
        self.sequenceSize = self.windowSize * 2 + 1
        self.windowStart = 0
        self.timer = None
        self.maxTimer = 1
        self.currentIndex = 0

    def connect(self, ip, port):
        super().send(ip, port, ("SYN:" + str(self.sequenceSize) + "," + str(self.windowSize)).encode())
        data, address = super().receive()
        if data.decode() == "SYN-ACK":
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

class Server(UDP_secure):
    def __init__(self, ip, port, buff):
        super().__init__(ip, port, buff)
        self.window = None

    def waitConnection(self):
        data, address = super().receive()
        message = (data.decode()).split(":")
        if message[0] == "SYN":
            message = message[1].split(",")
            self.sequenceSize = int(message[0])
            self.windowSize = int(message[1])
            self.windowStart = 0
            self.window = []
            for i in range(self.sequenceSize):
                self.window.append(False)
            super().send(address[0], address[1], b"SYN-ACK")
            data, address = super().receive()
            if data.decode() == "ACK":
                self.sdnIp = address[0]
                self.sdnPort = address[1]

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