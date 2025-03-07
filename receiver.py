import UDP_secure
from config import *

receiver = UDP_secure.Server(IP_receiver, port_receiver, buffer_receiver)
receiver.waitConnection()
receiver.receive()