#!/usr/local/bin/python

import socket
import json
import threading

def lidar_com_cliente(client_socket):
    """Lida com a comunicação com um cliente."""
    try:
        data = client_socket.recv(1024).decode('utf-8')
        json_data = json.loads(data)
        print("Objeto JSON recebido:", json_data)
        client_socket.send(json.dumps(json_data).encode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Erro ao decodificar objeto JSON recebido ou dados inválidos.")
        client_socket.send("Erro: Objeto JSON inválido ou dados inválidos.".encode('utf-8'))
    finally:
        client_socket.close()
        print("Conexão com o cliente encerrada.")

def iniciar_servidor(host, port):
    """Inicia um servidor TCP em uma porta específica."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Servidor TCP ouvindo em {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Cliente conectado em {port}: {addr}")
        client_thread = threading.Thread(target=lidar_com_cliente, args=(client_socket,))
        client_thread.start()

def main():
    host = '0.0.0.0'  # Endereço IP do servidor (localhost)
    ports = [80, 81]  # Portas para o servidor

    threads = []
    for port in ports:
        print("Inicia servidor em {host}:{port}")
        thread = threading.Thread(target=iniciar_servidor, args=(host, port))
        threads.append(thread)
        thread.start()

    # Aguarda as threads terminarem (opcional)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
