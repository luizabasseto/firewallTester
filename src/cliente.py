#!/usr/local/bin/python

import socket
import argparse
import json
import datetime
import os
import time
from datetime import datetime

from scapy.all import IP, ICMP, sr1

def ping(host, count):
    """Envia pacotes ICMP Echo Request e verifica a resposta."""
    received = 0
    print(f"\nPING {host}:")
    for seq in range(1, count + 1):
        packet = IP(dst=host) / ICMP()
        start_time = time.time()

        reply = sr1(packet, timeout=1, verbose=False)  # Envia o pacote e aguarda resposta

        if reply:
            elapsed_time = (time.time() - start_time) * 1000
            print(f"Resposta do {host}: Tempo = {elapsed_time:.2f} ms - {seq}/{count}")
            received += 1
        else:
            print(f"Sem resposta do {host} - {seq}/{count}")

        time.sleep(1)
    return received

def calcular_diferenca_timestamp(timestamp_envio, timestamp_recebido):
    """Calcula a diferença entre dois timestamps no formato ISO 8601 em milissegundos."""
    t1 = datetime.fromisoformat(timestamp_envio)
    t2 = datetime.fromisoformat(timestamp_recebido)
    diferenca = (t2 - t1).total_seconds() * 1000  # Converter para milissegundos
    return diferenca

# Configuração dos argumentos de linha de comando
parser = argparse.ArgumentParser(description="Cliente UDP/TCP/ICMP")
parser.add_argument("server_host", type=str, help="Endereço IP do servidor")
parser.add_argument("protocol", type=str.lower, help="Protocolo utilizado TCP/UDP/ICMP")
parser.add_argument("server_port", type=int, help="Porta do servidor")
parser.add_argument("testId", type=int, help="ID do teste")
parser.add_argument("timestamp", type=str, help="Timestamp do teste")

args = parser.parse_args()

# Inicializando socket de acordo com o protocolo
client_sock = None

if args.protocol == "udp":
    print("Protocolo: UDP")
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.settimeout(2)

elif args.protocol == "tcp":
    print("Protocolo: TCP")
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.settimeout(2)

elif args.protocol == "icmp":
    icmp_status = ping(args.server_host, args.server_port)
    client_port = 0  # ICMP não usa portas convencionais
else:
    print("Escolha um protocolo válido (TCP, UDP ou ICMP).")
    quit()

# Obtendo informações do cliente
client_host = socket.gethostname()
client_ip = socket.gethostbyname(client_host)
timestamp = datetime.now().isoformat()

# Criando diretório e nome do arquivo JSON
filename_timestamp = args.timestamp
dir_name = f"log/{filename_timestamp}"
filename = f"{dir_name}/test.json"
os.makedirs(dir_name, exist_ok=True)

# Carregando JSON existente ou criando um novo
try:
    with open(filename, 'r') as file:
        dados = json.load(file)
except:
    dados = {"tests": []}

# Criando estrutura do JSON
message = {
    "id": args.testId,
    "timestamp_teste": filename_timestamp,
    "timestamp_send": timestamp,
    "timestamp_recv": timestamp,
    "client_host": client_host,
    "client_ip": client_ip,
    "client_port": 0,
    "server_ip": args.server_host,
    "server_port": args.server_port,
    "protocol": args.protocol,
    "server_response": False
}

# Tratamento para ICMP
if args.protocol == "icmp":
    message["server_response"] = icmp_status > 0
    message["server_port"] = 8  # ICMP echo reply
    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)
    print(f"Gravando no arquivo: {json.dumps(message, indent=4)}")
    quit()

# Envio de dados (UDP e TCP)
json_message = json.dumps(message, indent=4)
server_address = (args.server_host, args.server_port)

try:
    print(f"Enviando: {json_message}")

    if args.protocol == "udp":
        client_sock.sendto(json_message.encode(), server_address)
    else:  # TCP
        client_sock.connect(server_address)
        client_sock.send(json_message.encode())

    try:
        response, _ = client_sock.recvfrom(1024) if args.protocol == "udp" else (client_sock.recv(1024), None)
        timestamp_response = datetime.now().isoformat()
        print(f"Tempo de ida e volta da mensagem: {calcular_diferenca_timestamp(message["timestamp_send"], timestamp_response)} ms")
        response_data = response.decode()
        #print(f"+ Resposta do servidor: {response_data}")
        message["timestamp_recv"] = timestamp_response
        message["server_response"] = True
    except socket.timeout:
        print("- Nenhuma resposta recebida do servidor.")

    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)
    print(f"Gravando no arquivo: {json.dumps(message, indent=4)}")

except (socket.gaierror, socket.herror, socket.timeout, ConnectionResetError, OSError) as e:
    print(f"Erro na comunicação: {e}")

finally:
    if client_sock:
        client_sock.close()
