import UDP_secure
from config import *

sender = UDP_secure.Client(IP_sender, port_sender, buffer_sender)
sender.send(IP_receiver, port_receiver, b"Hello, World!")
# sender.waitAck()