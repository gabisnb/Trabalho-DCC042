import socket
import time
import random
import base64
import traceback

from UDPSecure import UDPSecure



#? --------------Server Class--------------
class Receiver(UDPSecure):
    def __init__(self, ip, port, buff, file = 'data_rcv.bin'):
        super().__init__(ip, port, buff)
        self.availableBuff = buff
        self.wdn_max = self.availableBuff
        self.window_start = 0
        self.window = []
        self.pkts = []
        self.file_name = file
        self.file = None
        for i in range(self.wdn_max):
            self.window.append(False)

    def waitConnection(self):
        data, address, pktSize = super().receive()
        message = data.decode()
        if message == "SYN":
            super().send(address[0], address[1], ("SYN-ACK,"  + str(self.wdn_max)).encode())
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
            print(f"Enviando FIN-ACK para {address}")
            super().send(address[0], address[1], b"FIN-ACK")

            self.sdnIp = None
            self.sdnPort = None

            self.updateTimer()

            while time.time() - self.timer < self.maxTimer:
                try:
                    data, address, pktSize = super().receive()
                    if data.decode() == "ACK":
                        print("ACK recebido. Finalizando desconexão.")
                        return
                except Exception as e:
                    print(f"Erro ao receber pacote: {e}")
                    traceback.print_exc()
                    break  # Sai do loop se houver erro

            print("Tempo expirado ou erro detectado. Finalizando conexão.")

        except Exception as e:
            print(f"Erro em disconnect(): {e}")
            traceback.print_exc()

        finally:
            print("Chamando __del__() manualmente...")
            self.__del__()

    def receive(self):
        with open(self.file_name, 'r+b') as self.file:
            while True:
                try:
                    data, address, pktSize = super().receive()

                    if data.decode() == "FIN":
                        print("Recebido FIN. Iniciando desconexão.")
                        self.disconnect(address)
                        return
                    
                    metadata, message = self.extractMetadata(data)
                    sequenceNum = int(metadata[0])
                    self.window_size = int(metadata[1])*pktSize

                    # Simulação de perda de pacotes
                    if random.random() < 0.15:
                        print(f"Pacote {sequenceNum} perdido!")
                        continue  
                    
                    # Adiciona ao buffer o número de sequência, tamanho da mensagem e a mensagem
                    self.pkts.append([sequenceNum, pktSize - len(metadata), base64.b64decode(message.encode())])
                    
                    ack = self.markPkt(sequenceNum, pktSize)
                    self.send(address[0], address[1], ack.encode())

                except Exception as e:
                    print(f"Erro em receive(): {e}")
                    traceback.print_exc()
                    break

    def markPkt(self, index, pktSize):
        if self.isNotInWindow(index):
            if self.window[index]:
                return str(index) + ": Recebido!"
            return "Erro: Pacote fora da janela " + str(self.window_start) + " a " + str((self.window_start + pktSize-1)%self.wdn_max)
        for i in range(pktSize):
            self.window[(index + i)%self.wdn_max] = True
        self.availableBuff = self.availableBuff - pktSize
        self.moveWindow()
        nextPkt = str(index+pktSize%self.wdn_max)
        ack = nextPkt + "," + str(self.availableBuff) + ": Recebido!"
        return ack
    
    def moveWindow(self):
        i = self.window_start

        # Move início da janela até primeiro pacote não confirmado
        if self.window[i]:
            # prepara pacotes para serem carregados no arquivo
            self.pkts.sort()
        
        while self.window[i]:
            # self.window[i] = False
            if not (self.pkts) and i%len(self.pkts[1]) == 0:
                self.file.write(self.pkts.pop(0))
            self.window[(i+self.window_size)%self.wdn_max] = False
            self.availableBuff = self.availableBuff + 1
            i = (i+1)%self.wdn_max # Garante que i será um nº de sequência válido
        self.window_start = i
        
    def isNotInWindow(self, index):
        ''' Check if the index is not in the window '''
        wndSize = self.window_size   # get window size
        wndStart = self.window_start   # get window start
        wndEnd = (wndStart + wndSize)%self.wdn_max   # calculate window end

        afterWndStart  = wndEnd > wndStart and (index >= wndEnd or  index < wndStart)  # index is after the window end and window end is not at the beginning of the sequence
        beforeWndStart = wndEnd < wndStart and (index >= wndEnd and index < wndStart)  # index is before the window start and window end is at the beginning of the sequence

        # if index is after the window end and window end is not at the beginning of the sequence or
        # if index is before the window start and window end is at the beginning of the sequence, 
        #     return True
        return afterWndStart or beforeWndStart

    def __del__(self):
        super().__del__()