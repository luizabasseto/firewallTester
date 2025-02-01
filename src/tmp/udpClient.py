#!/usr/local/bin/python

import socket
import argparse
import json
import datetime
import os

# Configuração dos argumentos de linha de comando para o cliente
parser = argparse.ArgumentParser(description="Cliente UDP simples")
parser.add_argument("server_host", type=str, help="Endereço IP do servidor")
parser.add_argument("server_port", type=int, help="Porta do servidor")
parser.add_argument("testId", type=int, help="id do teste - numero inteiro")
parser.add_argument("timestamp", type=str, help="timestamp do teste")

args = parser.parse_args()

# Criação do socket UDP do cliente
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sock.bind(("", 0))  # Deixa o sistema escolher a porta de origem
client_sock.settimeout(2)  # Define tempo de espera para 2 segundos
client_port = client_sock.getsockname()[1]

# Obtendo informações do cliente
client_host = socket.gethostname()
client_ip = socket.gethostbyname(client_host)
timestamp = datetime.datetime.now().isoformat()
dt = datetime.datetime.fromisoformat(timestamp)
#filename_timestamp = dt.strftime("%Y%m%d-%H%M%S")
filename_timestamp = args.timestamp

# Criando diretório com filename_timestamp
dirName = "log/"+filename_timestamp
filename = "log/"+filename_timestamp+"/test.json"
os.makedirs(dirName, exist_ok=True)

# verifica se o arquivo existe, se existe carrega o objeto json, caso contrário cria
try:
    with open(filename, 'r') as arquivo:
        dados = json.load(arquivo)
except:
    dados = {"tests": []}
    #with open(filename, 'w') as arquivo:
    #    json.dump(dados, arquivo, indent=4)  # Escreve de volta com formatação

# Construindo objeto JSON
message = {
    "id": args.testId,
    "timestamp": filename_timestamp,
    "client_host": client_host,
    "client_ip": client_ip,
    "client_port": client_port,
    "server_ip": args.server_host,
    "server_port": args.server_port,
    "server_response": False
}

json_message = json.dumps(message, indent=4)
server_address = (args.server_host, args.server_port)

print(f"Enviando: {json_message}")
client_sock.sendto(json_message.encode(), server_address)

try:
    response, _ = client_sock.recvfrom(1024)
    response_data = response.decode()
    print(f"+ Resposta do servidor: {response_data}")
    message["server_response"] = True
    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)
except socket.timeout:
    print("- Nenhuma resposta recebida do servidor.")
    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)
    print(f"Gravando no arquivo: {json_message}")

client_sock.close()
