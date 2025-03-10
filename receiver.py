from Receiver import Receiver
from config import *

receiver = Receiver(IP_receiver, port_receiver, buffer_receiver)
receiver.waitConnection()
receiver.receive()
