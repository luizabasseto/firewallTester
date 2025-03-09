#!/usr/local/bin/python

import socket
import json
import argparse

# Configuração dos argumentos de linha de comando para o cliente
parser = argparse.ArgumentParser(description="Cliente UDP simples")
parser.add_argument("server_host", type=str, help="Endereço IP do servidor")
parser.add_argument("server_port", type=int, help="Porta do servidor")
parser.add_argument("testId", type=int, help="id do teste - numero inteiro")
parser.add_argument("timestamp", type=str, help="timestamp do teste")

args = parser.parse_args()
host = args.server_host  # Endereço IP do servidor (localhost)
port = args.server_port  # Porta do servidor

# Cria o socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta-se ao servidor
client_socket.connect((host, port))

# Cria um objeto JSON de exemplo
data = {
    "nome": "João",
    "idade": 30,
    "cidade": "São Paulo"
}

# Envia o objeto JSON para o servidor
client_socket.send(json.dumps(data).encode('utf-8'))

# Recebe a resposta do servidor
response = client_socket.recv(1024).decode('utf-8')

try:
    # Decodifica a resposta JSON do servidor
    json_response = json.loads(response)
    print("Resposta do servidor:", json_response)

except json.JSONDecodeError:
    print("Erro ao decodificar resposta JSON do servidor:", response)

# Fecha a conexão com o servidor
client_socket.close()
