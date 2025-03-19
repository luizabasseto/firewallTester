#!/usr/local/bin/python

import socket
import json
import threading
import sys
import psutil
import os
import signal
import time

total_udp_msgs = 0
total_tcp_msgs = 0
server_ips = []
server_name = "noName"

def get_ips():
    server_ips = []
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family in (2, 10):  # 2 = IPv4, 10 = IPv6
                if not addr.address.startswith("127."):  # Exclui localhost
                    server_ips.append(addr.address)
    return server_ips

def read_ports_from_file(nome_arquivo):
    """
    Lê um arquivo com tuplas porta/protocolo (uma por linha) e retorna uma lista de tuplas.

    Args:
        nome_arquivo (str): O nome do arquivo a ser lido.

    Returns:
        list: Uma lista de tuplas (porta, protocolo) ou None em caso de erro.
    """
    try:
        with open(nome_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()

        tuplas = []
        for linha in linhas:
            linha = linha.strip()  # Remove espaços em branco extras
            if linha: # Verifica se a linha não está vazia
                try:
                    porta_proto = linha.split('/')
                    if len(porta_proto) == 2:
                        porta = int(porta_proto[0])
                        protocolo = porta_proto[1].lower() # Converte para maiúsculo para consistência
                        tuplas.append((porta, protocolo))
                    else:
                        print(f"Error: Invalid line: '{linha}'. Format must be port/protocol.")

                except ValueError:
                    print(f"Error: Invalid port in line: '{linha}'. Must be an integer.")

        return tuplas

    except FileNotFoundError:
        print(f"Error: File  '{nome_arquivo}' not found.")
        return None

def get_pid_by_port(protocol, port):
    """Retorna o PID do processo que está usando a porta especificada."""
    print(f"Get process pid on port {port}.")
    for conn in psutil.net_connections(kind=protocol):
        if conn.laddr.port == port:
            return conn.pid
    return None

def kill_pid_by_port(protocol, port):
    """Mata um processo que está rodando em uma porta via pid"""
    print(f"Kill process on port {port}.")
    pid = get_pid_by_port(protocol, port)
    if  pid != None:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Process {pid} successfully terminated.")

        except Exception as e:
            print(f"Error terminating process {pid}: {e}")

def show_total_msgs():
    global total_tcp_msgs, total_udp_msgs
    print(f"Number of messages:\n\t * TCP: {total_tcp_msgs};\n\t * UDP: {total_udp_msgs};\n\t * Total: {total_tcp_msgs+total_udp_msgs};")

# TODO - alterar o objeto json enviado pelo cliente, caso a mensagem esteja com um IP diferente do host de destino, isso significa que a mensagem passou por um nat, então seria legal colocar o IP/porta do host que recebeu e tratou a informação para informar que o DNAT foi bem sucessido ou não - isso tem que ser feito para tcp e udp.
def lidar_com_cliente_TCP(client_socket):
    """Lida com a comunicação com um cliente."""
    global total_tcp_msgs
    try:
        data = client_socket.recv(1024).decode('utf-8')
        total_tcp_msgs += 1
        json_data = json.loads(data)
        print(f"Received JSON object:\n", json.dumps(json_data, indent=4))

        dest_ip = json_data["server_ip"]
        if dest_ip not in server_ips:
            json_data["message"] = f"DNAT to {server_name}"

        client_socket.send(json.dumps(json_data).encode('utf-8'))

    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Error decoding received JSON object or invalid data.")
        client_socket.send("Error: Invalid JSON object or invalid data.".encode('utf-8'))

    finally:
        client_socket.close()
        print("Connection with client closed.")
        show_total_msgs()

def servidor_UDP(port):
    """Inicia servidor UDP."""
    global total_udp_msgs
    host = '0.0.0.0'
    protocol = 'udp'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))  # Bind para o endereço local e porta

    while True:
        data, addr = sock.recvfrom(1024)  # Recebe até 1024 bytes de dados
        total_udp_msgs += 1
        print(f"Message received from {addr}: {data.decode()}")

        # Enviar uma resposta opcional
        response = f"Received: {data.decode()}"
        sock.sendto(response.encode(), addr)
        show_total_msgs()

def iniciar_servidor(host, protocol, port):
    """Inicia um servidor TCP ou UDP em uma porta específica."""
    if protocol == "tcp":
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"\t++ Listening on port  {protocol.upper()}/{port}")

        except OSError as e:
            print(f"Error executing server {host}-{protocol}:{port} - check if the port is not in use by another service!!!")
            print(f"\t{e}")
            quit()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Client connected on {port}: {addr}")
            client_thread = threading.Thread(target=lidar_com_cliente_TCP, args=(client_socket,))
            client_thread.start()

    elif protocol == "udp":
            print(f"\t++ Listening on port {protocol.upper()}/{port}")
            client_thread = threading.Thread(target=servidor_UDP, args=(port,))
            client_thread.start()

    else:
        print(f">>> WARNING!!! Could not start this port: {protocol}/{port}")


def main():
    server_name = psutil.users()[0].host
    host = '0.0.0.0'  # Endereço IP do servidor (localhost)
    #ports = [5000, 5001]  # Portas para o servidor
    threads = []
    nome_arquivo = "conf/portas.conf"  # Substitua pelo nome do seu arquivo
    tuplas = read_ports_from_file(nome_arquivo)
    print(f"Starting servers with ports present in file: {nome_arquivo} - This file must contain lines with port/protocol, example 80/tcp.")
    if tuplas:
        print("Tuples read from file:")
        #for porta, protocolo in tuplas:
        #    print(f"Porta: {porta}, Protocolo: {protocolo}")

        # Exemplo de como acessar os dados individualmente:
        for port, protocol in tuplas:
            # Faça algo com a porta e o protocolo...
            if protocol == "tcp" or protocol == "udp":
                print(f"Starting {port}/{protocol}")
                kill_pid_by_port(protocol, port)
                thread = threading.Thread(target=iniciar_servidor, args=(host, protocol, port), daemon=True)
                threads.append(thread)
                thread.start()
            #elif protocolo == "udp":
            #    print(f"Porta UDP: {porta}")
            else:
                print(f"Protocol not supported: {protocol}")


    else:
        print(f"Could not read ports and protocols from file {nome_arquivo}.")

    time.sleep(3)
    print("\nIf needed, press Ctrl+C to terminate the program.")
    try:
        while True:
            time.sleep(1)  # Mantém o programa principal rodando
    except KeyboardInterrupt:
        print("\nProgram terminated with Ctrl+C.")

if __name__ == "__main__":
    main()
