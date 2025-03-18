import socket
import time
import random
import asyncio
import threading
import os
import base64

from UDPSecure import UDPSecure


#? --------------Sender Class--------------
class Sender(UDPSecure):
    def __init__(self, ip, port, buff):
        super().__init__(ip, port, buff)
        self.wdn_max = 0
        self.window_start = 0
        self.pktSize = 32
        self.timer = None
        self.maxTimer = 1
        self.currentIndex = 0
        self.threads = []
        
        # Congestion Control Variables
        self.window_size = 1  # Start with 1 packet
        self.ssthresh = 8  # Initial slow start threshold (adjustable)
        self.dup_ack_count = 0
        self.last_ack = -1  # Track last acknowledged packet

    def connect(self, ip, port):
        super().send(ip, port, b"SYN")
        data, address, pktSize = super().receive()
        messages = data.decode().split(",")
        if messages[0] == "SYN-ACK":
            self.wdn_max = int(messages[1])
            self.window_start = 0
            self.rcvIp = ip
            self.rcvPort = port
            super().send(ip, port, b"ACK")
            print("Números de sequencia:" + str(self.wdn_max))

    def disconnect(self):
        try:
            super().send(self.rcvIp, self.rcvPort, b"FIN")
            data, address, pktSize = super().receive()
            if data.decode() == "FIN-ACK":
                super().send(self.rcvIp, self.rcvPort, b"ACK")
        except Exception as e:
            print(Exception)

    def sendFile(self, file):
        with open(file, "rb") as f:
            file_size = os.path.getsize(file)
            print(file_size)
            chunks_sent = 0
            for _ in range(int(file_size/self.pktSize)):
                for i in range(self.window_size):
                    chunk = f.read(self.pktSize)
                    if not chunk:
                        break
                    chunk = base64.b64encode(chunk)
                    self.threads.append(threading.Thread(target=self.send, args=(chunk,)))
                    self.threads[i].start()
                    chunks_sent = chunks_sent + 1
                    self.currentIndex = _ % self.wdn_max
                if self.threads:
                    result = self.threads.pop(0).join(self.maxTimer)
                    if result != None and not (result.is_alive()):
                        self.handle_loss()
                    i = 1
                    while i < self.window_size and self.threads:
                        self.threads.pop(0).join()
                        i = i+1

            


    def send(self, message):
        if self.window_size <= 0:
            return  # Avoid sending if congestion window is 0
        
        data = (str(self.currentIndex) + "," + str(self.window_size) + ":").encode() + message
        super().send(self.rcvIp, self.rcvPort, data)
        self.timer = time.time()
        error, ack = self.waitAck()
        
        if error:
            self.handle_loss()
        else:
            self.handle_ack(ack)

    def waitAck(self):
        """Wait for an ACK and check for duplicate ACKs."""
        while time.time() - self.timer < self.maxTimer:
            data, address, pktSize = super().receive()
            metadata, bin_data = self.extractMetadata(data)

            if metadata[0] == "Erro":
                print(metadata)
                return True, None  # Packet loss detected
            
            sequenceNum = int(metadata[0])
            
            if sequenceNum == self.last_ack:
                self.dup_ack_count += 1
                if self.dup_ack_count == 3:
                    self.handle_fast_retransmit()
                    return False, sequenceNum  # Stop waiting once fast retransmit happens
            else:
                self.dup_ack_count = 0  # Reset counter
                self.last_ack = sequenceNum

            return False, sequenceNum  # Return False if ACK is valid
        
        return True, None  # Timeout case


    def handle_loss(self):
        """Handles congestion event (packet loss)."""
        print("Packet loss detected! Reducing congestion window.")
        self.ssthresh = max(self.window_size // 2, 1)
        
        # 🚀 Reno: Set window_size to ssthresh instead of 1
        self.window_size = self.ssthresh  
        self.dup_ack_count = 0


    def handle_fast_retransmit(self):
        """Handles Fast Retransmit when three duplicate ACKs are received."""
        print("Fast retransmit triggered! Halving congestion window.")
        self.ssthresh = max(self.window_size // 2, 1)
        self.window_size = self.ssthresh  # Reduce window_size but avoid slow start
        self.dup_ack_count = 0  # Reset duplicate ACK counter


    def handle_ack(self, ack):
        """Handles successful ACK reception and updates congestion control."""
        if self.window_size < self.ssthresh:
            # Slow Start Phase: Exponential Growth
            self.window_size *= 2
        else:
            # Congestion Avoidance Phase: Linear Growth
            self.window_size += 1
        
        self.window_size = min(self.window_size, self.wdn_max)
        self.dup_ack_count = 0  # Reset duplicate ACK counter
        print(f"Updated window_size: {self.window_size}, ssthresh: {self.ssthresh}")

    def moveWindow(self, index):
        self.window_start = (index + 1) % self.wdn_max

    def markPkt(self, index):
        # if self.isNotInWindow(index):
        #     return "Erro: Pacote fora da janela " + str(self.window_start) + " a " + str((self.window_start + self.windowSize-1)%self.wdn_max)
        previousStart = self.window_start
        self.window_start = index
        self.updateTimer()
        return str(previousStart) + " a " + str(index-1%self.wdn_max) + ": Recebido!"
    
    def __del__(self):
        self.disconnect()
        super().__del__()
