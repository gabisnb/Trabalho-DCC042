import threading
import time
import random
from Sender import Sender
from Receiver import Receiver
from config import *
import base64

# Configurações
data_file = "test_data.bin"
NUM_PACKETS = 1000

# Criar arquivo de 10MB para simulação
def generate_data_file():
    print("Gerando arquivo de teste...")
    with open(data_file, "wb") as f:
        f.write(bytearray(random.getrandbits(8) for _ in range(NUM_PACKETS * buffer_receiver)))
    print("Arquivo gerado com sucesso!")

# Função para iniciar o Receiver (Servidor)
def start_receiver():
    global receiver  # Make receiver accessible globally
    receiver = Receiver(IP_receiver, port_receiver, buffer_receiver)
    print("Receiver iniciado. Aguardando pacotes...")
    receiver.waitConnection()
    receiver.receive()

# Função para iniciar o Sender (Cliente) e enviar o arquivo
def start_sender():
    sender = Sender(IP_sender, port_sender, buffer_sender)
    sender.connect(IP_receiver, port_receiver)

    sender.sendFile(data_file, NUM_PACKETS)
    
    sender.disconnect()
    print("Envio finalizado.")

# Criar e iniciar as threads
generate_data_file()
receiver_thread = threading.Thread(target=start_receiver)
sender_thread = threading.Thread(target=start_sender)

receiver_thread.start()
time.sleep(1)  # Pequeno delay para garantir que o receiver esteja pronto
sender_thread.start()

sender_thread.join()
receiver_thread.join()

# Print the total packet loss at the end
print(f"Avaliação concluída! Total de pacotes perdidos: {receiver.lost_packet_count}")
