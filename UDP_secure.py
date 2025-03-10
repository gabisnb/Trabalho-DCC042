import socket







#? --------------UDP_secure Class--------------
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

