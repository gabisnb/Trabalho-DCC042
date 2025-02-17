import UDP_secure
from config import *

receiver = UDP_secure.UDP_secure(IP_receiver, port_receiver, buffer_receiver)
receiver.receive(IP_sender)