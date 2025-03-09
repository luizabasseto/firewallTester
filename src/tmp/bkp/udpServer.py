#!/usr/local/bin/python

import socket
import argparse

# Configuração dos argumentos de linha de comando
parser = argparse.ArgumentParser(description="Servidor UDP simples")
parser.add_argument("port", type=int, help="Porta do servidor")
args = parser.parse_args()

# Definição do endereço e porta do servidor
HOST = "0.0.0.0"
PORT = args.port

# Criação do socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Servidor UDP iniciado em {HOST}:{PORT}")

while True:
    data, addr = sock.recvfrom(1024)  # Recebe até 1024 bytes de dados
    print(f"Mensagem recebida de {addr}: {data.decode()}")
    
    # Enviar uma resposta opcional
    response = f"Recebido: {data.decode()}"
    sock.sendto(response.encode(), addr)
