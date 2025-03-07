import UDP_secure
from config import *

sender = UDP_secure.Client(IP_sender, port_sender, buffer_sender)
key = ""
sender.connect(IP_receiver, port_receiver)
while key != "exit":
    key = input("Enviar próxima? (exit para sair, enter para confirmar)")
    sender.send(IP_receiver, port_receiver, b"Hello, World!")
sender.disconnect()
# sender.waitAck()