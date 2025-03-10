from Server import Server
from config import *

receiver = Server(IP_receiver, port_receiver, buffer_receiver)
receiver.waitConnection()
receiver.receive()
