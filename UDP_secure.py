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
        self.windowSize = 8
        self.sequenceSize = self.windowSize * 2 + 1
        self.windowStart = 0
        self.window = []
        for i in range(self.sequenceSize):
            self.window.append(False)

    def send(self, ip, port, data):
        self.socket.sendto(data, (ip, port))
        print("Enviou '" + data.decode() + "' com sucesso")

    def markPkt(self, index):
        if self.isNotInWindow(index):
            return "Erro: Pacote fora da janela " + str(self.windowStart) + " a " + str((self.windowStart + self.windowSize-1)%self.sequenceSize)
        self.window[index] = True
        if self.windowStart == index:
            self.moveWindow()
        return str(index) + ":" + "Recebido!"

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
    
    def moveWindow(self):
        i = self.windowStart

        # Move início da janela até primeiro pacote não confirmado
        while self.window[i] != False:
            self.window[i] = False
            i = (i+1)%self.sequenceSize # Garante que i será um nº de sequência válido
        self.windowStart = i

    def __del__(self):
        self.socket.close()

class Client(UDP_secure):
    def __init__(self, ip, port, buff):
        super().__init__(ip, port, buff)
        self.timer = None
        self.maxTimer = 1
        self.currentIndex = 0

    def send(self, ip, port, data):
        data = (str(self.currentIndex) + ":").encode() + data
        super().send(ip, port, data)
        
        if self.timer == None:
            self.timer = time.time()
        error = self.waitAck()
        if error:
            return
        self.currentIndex = (self.currentIndex + 1) % self.sequenceSize

    def waitAck(self):
        while time.time() - self.timer < self.maxTimer:
            data, address = self.socket.recvfrom(self.port)
            print("Received:", data, "from", address, "in", time.time() - self.timer)
            message = (data.decode()).split(":")[0]
            if message == "Erro":
                print(data.decode())
                return True
            sequenceNum = int(message)
            self.markPkt(sequenceNum)
            break
        return False

class Server(UDP_secure):
    def __init__(self, ip, port, buff):
        super().__init__(ip, port, buff)
    
    def receive(self, from_ip):
        self.socket.bind((from_ip, self.port))
        while True:
            data, address = self.socket.recvfrom(self.buffer)
            print("Received:", data, "from", address)
            sequenceNum = int((data.decode()).split(":")[0])
            ack = self.markPkt(sequenceNum)
            self.send(address[0], address[1], (ack).encode())