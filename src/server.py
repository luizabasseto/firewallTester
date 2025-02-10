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
                        print(f"Erro: Linha inválida: '{linha}'. Formato deve ser porta/protocolo.")

                except ValueError:
                    print(f"Erro: Porta inválida na linha: '{linha}'. Deve ser um número inteiro.")

        return tuplas

    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        return None

def get_pid_by_port(protocol, port):
    """Retorna o PID do processo que está usando a porta especificada."""
    print(f"Obter pid do processo na porta {port}.")
    for conn in psutil.net_connections(kind=protocol):
        if conn.laddr.port == port:
            return conn.pid
    return None

def kill_pid_by_port(protocol, port):
    """Mata um processo que está rodando em uma porta via pid"""
    print(f"Matar processo na porta {port}.")
    pid = get_pid_by_port(protocol, port)
    if  pid != None:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Processo {pid} finalizado com sucesso.")

        except Exception as e:
            print(f"Erro ao finalizar o processo {pid}: {e}")

def show_total_msgs():
    global total_tcp_msgs, total_udp_msgs
    print(f"Quantidade de mensagens:\n\t * TCP: {total_tcp_msgs};\n\t * UDP: {total_udp_msgs};\n\t * Total: {total_tcp_msgs+total_udp_msgs};")

def lidar_com_cliente_TCP(client_socket):
    """Lida com a comunicação com um cliente."""
    global total_tcp_msgs
    try:
        data = client_socket.recv(1024).decode('utf-8')
        total_tcp_msgs += 1
        json_data = json.loads(data)
        print(f"Objeto JSON recebido:\n", json.dumps(json_data, indent=4))
        client_socket.send(json.dumps(json_data).encode('utf-8'))

    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Erro ao decodificar objeto JSON recebido ou dados inválidos.")
        client_socket.send("Erro: Objeto JSON inválido ou dados inválidos.".encode('utf-8'))

    finally:
        client_socket.close()
        print("Conexão com o cliente encerrada.")
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
        print(f"Mensagem recebida de {addr}: {data.decode()}")

        # Enviar uma resposta opcional
        response = f"Recebido: {data.decode()}"
        sock.sendto(response.encode(), addr)
        show_total_msgs()

def iniciar_servidor(host, protocol, port):
    """Inicia um servidor TCP ou UDP em uma porta específica."""
    if protocol == "tcp":
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"\t++ Escutando na porta {protocol.upper()}/{port}")

        except OSError as e:
            print(f"Erro ao executar servidor {host}-{protocol}:{port} - verifique se a porta não está em uso por outro serviço!!!")
            print(f"\t{e}")
            quit()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Cliente conectado em {port}: {addr}")
            client_thread = threading.Thread(target=lidar_com_cliente_TCP, args=(client_socket,))
            client_thread.start()

    elif protocol == "udp":
            print(f"\t++ Escutando na porta {protocol.upper()}/{port}")
            client_thread = threading.Thread(target=servidor_UDP, args=(port,))
            client_thread.start()

    else:
        print(f">>> ATENÇÃO!!! Não foi possível iniciar essa porta: {protocol}/{port}")


def main():
    host = '0.0.0.0'  # Endereço IP do servidor (localhost)
    #ports = [5000, 5001]  # Portas para o servidor
    threads = []
    nome_arquivo = "conf/portas.conf"  # Substitua pelo nome do seu arquivo
    tuplas = read_ports_from_file(nome_arquivo)
    print(f"Iniciando servidores com portas presentes no arquivo: {nome_arquivo} - Esse arquivo deve conter linhas com porta/protocolo, exemplo 80/tcp")
    if tuplas:
        print("Tuplas lidas do arquivo:")
        #for porta, protocolo in tuplas:
        #    print(f"Porta: {porta}, Protocolo: {protocolo}")

        # Exemplo de como acessar os dados individualmente:
        for port, protocol in tuplas:
            # Faça algo com a porta e o protocolo...
            if protocol == "tcp" or protocol == "udp":
                print(f"Iniciando {port}/{protocol}")
                kill_pid_by_port(protocol, port)
                thread = threading.Thread(target=iniciar_servidor, args=(host, protocol, port), daemon=True)
                threads.append(thread)
                thread.start()
            #elif protocolo == "udp":
            #    print(f"Porta UDP: {porta}")
            else:
                print(f"Protocolo não suportado {protocol}")


    else:
        print(f"Não foi possível ler as portas e protocolos do arquivo {nome_arquivo}.")

    #threads = []
    #for port in ports:
    #    print("Inicia servidor em {host}:{port}")
    #    kill_pid_by_port('tcp', port)
    #    thread = threading.Thread(target=iniciar_servidor, args=(host, port), daemon=True)
    #    threads.append(thread)
    #    thread.start()

    time.sleep(3)
    print("\nSe precisar, pressione Ctrl+C para encerrar o progrma.")
    try:
        while True:
            time.sleep(1)  # Mantém o programa principal rodando
    except KeyboardInterrupt:
        print("\nPrograma encerrado com Ctrl+C.")

if __name__ == "__main__":
    main()
