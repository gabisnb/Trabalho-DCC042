from Sender import Sender
from config import *

sender = Sender(IP_sender, port_sender, buffer_sender)
key = ""
sender.connect(IP_receiver, port_receiver)
while key != "exit":
    key = input("Enviar próxima? (exit para sair, enter para confirmar)")
    sender.send(b"Hello, World!")
