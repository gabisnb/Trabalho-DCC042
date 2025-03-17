import threading
import time
import random
from sender import Sender
from receiver import Receiver

# Configurações
data_file = "test_data.bin"
IP = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024
NUM_PACKETS = 10000

# Criar arquivo de 10MB para simulação
def generate_data_file():
    print("Gerando arquivo de teste...")
    with open(data_file, "wb") as f:
        f.write(bytearray(random.getrandbits(8) for _ in range(NUM_PACKETS * BUFFER_SIZE)))
    print("Arquivo gerado com sucesso!")

# Função para iniciar o Receiver (Servidor)
def start_receiver():
    receiver = Receiver(IP, PORT, BUFFER_SIZE)
    print("Receiver iniciado. Aguardando pacotes...")
    receiver.receive()

# Função para iniciar o Sender (Cliente) e enviar o arquivo
def start_sender():
    sender = Sender(IP, PORT, BUFFER_SIZE)
    sender.connect(IP, PORT)
    
    with open(data_file, "rb") as f:
        for _ in range(NUM_PACKETS):
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sender.send(IP, PORT, chunk)
            time.sleep(0.001)  # Pequeno delay para simular transmissão real
    
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

print("Avaliação concluída!")