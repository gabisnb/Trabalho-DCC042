import socket
import time
import asyncio






#? --------------UDP_secure Class--------------
class UDPSecure:
    def __init__(self, ip, port, buff):
        self.ip = ip
        self.port = port
        self.buffer = buff
        self.protocol = socket.SOCK_DGRAM
        self.timer = 0.0
        self.maxTimer = 3.0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        

    def updateTimer(self):
        ''' Update the timer '''
        self.timer = time.time()


    def waitAck(self):
        ''' Wait for an ACK message from the receiver '''
        # não estourou o temporizador
        # while time.time() - self.timer < self.maxTimer:
        #     data, address = self.receive()
        print(f"Waiting for ACK... Time elapsed: {time.time() - self.timer:.2f}")
        self.socket.settimeout(self.maxTimer)  # Set timeout
        try:
            data, address = self.socket.recvfrom(self.buffer)
        except socket.timeout:
            print("Timeout occurred! No ACK received.")
            return True  # Indicate timeout



    def send(self, ip, port, data):
        self.socket.sendto(data, (ip, port))
        print("Enviou '" + data.decode()[:10] + "' com sucesso")


    def receive(self):
        data, address = self.socket.recvfrom(self.buffer)
        pktSize = len(data)
        print("Recebeu:", data[:10], "de", address)
        return data, address, pktSize
    
    def extractMetadata(self, data):
        components = (data.decode()).split(":")
        metadata = components[0].split(",")
        return metadata, components[1].encode()


    def isNotInWindow(self, index):
        ''' Check if the index is not in the window '''
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

