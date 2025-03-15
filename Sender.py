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
        
        # Congestion Control Variables
        self.cwnd = 1  # Start with 1 packet
        self.ssthresh = 8  # Initial slow start threshold (adjustable)
        self.dup_ack_count = 0
        self.last_ack = -1  # Track last acknowledged packet

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
        if self.cwnd <= 0:
            return  # Avoid sending if congestion window is 0
        
        data = (str(self.currentIndex) + ":").encode() + data
        if self.currentIndex == self.windowStart:
            self.timer = time.time()
        super().send(ip, port, data)
        self.timer = time.time()
        error, ack = self.waitAck()
        
        if error:
            self.handle_loss()
        else:
            self.handle_ack(ack)
        
        self.currentIndex = (self.currentIndex + 1) % self.sequenceSize

    def waitAck(self):
        """Wait for an ACK and check for duplicate ACKs."""
        while time.time() - self.timer < self.maxTimer:
            data, address = super().receive()
            message = data.decode().split(":")[0]
            
            if message == "Erro":
                print(data.decode())
                return True, None
            
            sequenceNum = int(message)
            if sequenceNum == self.last_ack:
                self.dup_ack_count += 1
                if self.dup_ack_count == 3:
                    self.handle_fast_retransmit()
            else:
                self.dup_ack_count = 0
                self.last_ack = sequenceNum
            
            return False, sequenceNum
        
        return True, None

    def handle_loss(self):
        """Handles congestion event (packet loss)."""
        print("Packet loss detected! Reducing congestion window.")
        self.ssthresh = max(self.cwnd // 2, 1)
        self.cwnd = 1  # Reset to slow start
        self.dup_ack_count = 0

    def handle_fast_retransmit(self):
        """Handles Fast Retransmit when three duplicate ACKs are received."""
        print("Fast retransmit triggered! Halving congestion window.")
        self.ssthresh = max(self.cwnd // 2, 1)
        self.cwnd = self.ssthresh  # Reduce cwnd but avoid slow start
        self.dup_ack_count = 0  # Reset duplicate ACK counter

    def handle_ack(self, ack):
        """Handles successful ACK reception and updates congestion control."""
        if self.cwnd < self.ssthresh:
            # Slow Start Phase: Exponential Growth
            self.cwnd *= 2
        else:
            # Congestion Avoidance Phase: Linear Growth
            self.cwnd += 1
        
        self.dup_ack_count = 0  # Reset duplicate ACK counter
        print(f"Updated cwnd: {self.cwnd}, ssthresh: {self.ssthresh}")

    def moveWindow(self, index):
        self.windowStart = (index + 1) % self.sequenceSize

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
