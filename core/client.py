#!/usr/local/bin/python

"""
    Program Name: Firewall Tester - Client
    Description: Acts as a client so that the firewall rule testing software can send packets to the server software in the test scenario.
    Author: Luiz Arthur Feitosa dos Santos - luiz.arthur.feitosa.santos@gmail.com / luizsantos@utfpr.edu.br
    License: GNU General Public License v3.0
    Version: 1.0
"""

import socket
import argparse
import json
import datetime
import os
import time
from datetime import datetime

from scapy.all import IP, ICMP, sr1
# TODO - Fazer essa validação para todos logo no inicio, se não passar nem inicia os testes - colocar uma msg no status
def validar_host(host):
    try:
        socket.gethostbyname(host)  # Tenta resolver o nome do host
        return True  # Host válido
    except socket.gaierror:
        return False  # Host inválido

def ping(host, count):
    """Envia pacotes ICMP Echo Request e verifica a resposta."""
    received = 0
    count = 1 # ignora a quantidade de msg passada pelo usuário, pois na interface essa é a porta e por exemplo a porta é 80 serão 80 pings...
    if verbose > 0: print(f"\nPING {host}:")
    for seq in range(1, count + 1):
        if not validar_host(host):
            #print(f"Erro: O host {host} não é valido no cliente no módulo scapy")
            return -1 # TODO - colocar o valor -1 para caso de erro e colocar uma msg no status

        packet = IP(dst=host) / ICMP()
        start_time = time.time()

        reply = sr1(packet, timeout=1, verbose=False)  # Envia o pacote e aguarda resposta

        if reply:
            elapsed_time = (time.time() - start_time) * 1000
            if verbose > 0: print(f"\033[32m\t+ Response from {host}: Time = {elapsed_time:.2f} ms - {seq}/{count}\033[0m")
            received += 1
        else:
            if verbose > 0: print(f"\033[31m\t- No response from {host} - {seq}/{count}\033[0m")

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
parser.add_argument("verbose", type=int, help="Nível de verbose - 0,1,2 quanto maior o valor mais detalhes")

args = parser.parse_args()
verbose = args.verbose

# Inicializando socket de acordo com o protocolo
client_sock = None
client_port = -1

if args.protocol.lower() == "udp" or args.protocol.lower() == "UDP":
    if verbose > 0: print("Protocol: UDP")
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.bind(("", 0))
    client_sock.settimeout(2)
    client_port = client_sock.getsockname()[1]

elif args.protocol.lower() == "tcp" or args.protocol.lower() == "TCP":
    if verbose > 0: print("Protocol: TCP")
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.bind(("", 0))
    client_sock.settimeout(2)
    client_port = client_sock.getsockname()[1]


elif args.protocol.lower() == "icmp" or args.protocol.lower() == "ICMP":
    if verbose > 0: print("Protocol: ICMP")
    icmp_status = ping(args.server_host, args.server_port)
    client_port = 0  # ICMP não usa portas convencionais
else:
    if verbose > 0: print("Choose a valid protocol (TCP, UDP ou ICMP).")
    quit()

# Obtendo informações do cliente
# TODO - se o nome do host estiver errado no arquivo /etc/host esse programa não funciona! Bem isso está aqui para pegar o ip do cliente, então não sei se precisa pegar o nome para pegar o IP - ver como fazer isso só pegando o IP - ai uma questão que teria, seria se o cliente tiver mais que um IP.
client_host = socket.gethostname()
client_ip = socket.gethostbyname(client_host) # TODO - se o IP for 0.0.0.0 significa que o host de destino não tem IP, inserir isso no resultado - melhor nem executar a conexão, ou seja, terminar antes e já colocar no objeto json que houve erro.
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
# status - é caso aconteça algo, tal como o pacote não pode ser enviado pois o host cliente não tem rota!
# message - pode ser utilizada para simular, por exemplo o envio de uma mensagem maliciosa na camada de aplicação, tal como com: com uso de palavras impróprias (porn, hacker, etc) ou termos suspeitos ("/etc/shadow")
message = {
    "id": args.testId,
    "timestamp_teste": filename_timestamp,
    "timestamp_send": timestamp,
    "timestamp_recv": timestamp,
    "client_host": client_host,
    "client_ip": client_ip,
    "client_port": client_port,
    "server_ip": args.server_host,
    "server_port": args.server_port,
    "protocol": args.protocol,
    "server_response": False,
    "status" : '0',
    "status_msg": 'ok',
    "message" : 'Test successfully completed'
}
# se o status for zero, ocorreu tudo bem, caso contrário deu algum erro ,tal como:
#  1 - erro de rede

# Tratamento para ICMP
if args.protocol == "icmp":
    if icmp_status < 0:
        # TODO - se o firewall barrar, está dando que é erro! mas foi o firewall, tinha que ver se há como identificar quando é erro e quando é o firewall, por agora vai ficar o status em 0
        #message["status"] = "1"
        message["status"] = "0"
        message["status_msg"] = "Firewall Drop or Host desconhecido"
    else:
        message["server_response"] = icmp_status > 0
        message["server_port"] = 8  # ICMP echo reply
        
    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)
    if verbose > 0: print(f"Writing to file: {json.dumps(message, indent=4)}")
    # envia icmp para a gui
    print(json.dumps(message, indent=4))
    quit()

# Envio de dados (UDP e TCP)
json_message = json.dumps(message, indent=4)
server_address = (args.server_host, args.server_port)

try:
    if verbose > 0: print(f"-> Sending message to: {args.server_host}:{args.server_port}/{args.protocol.upper()}.")
    if verbose > 0: print(f"Sending: {json_message}")
    
    if args.server_host == "0.0.0.0":
        message["status_msg"] = "Error by using destination IP 0.0.0.0"
    else:
        if args.protocol == "udp":
            client_sock.sendto(json_message.encode(), server_address)
        else:  # TCP
            client_sock.connect(server_address)
            client_sock.send(json_message.encode())
            # pega o IP do cliente que realmente foi utilizado na transmissão
            client_ip = client_sock.getsockname()[0]
        # TODO - o cliente não está mostrando o json que o server está enviando alterado! para mostrar o DNAT
        # TODO - ver se compensa colocar o campo NAT para indicar um possível nat - atualmente está no campo message
        try:
            response, _ = client_sock.recvfrom(1024) if args.protocol == "udp" else (client_sock.recv(1024), None)
            timestamp_response = datetime.now().isoformat()
            if verbose > 0: print(f"\033[32m\t+ Response received from the server {args.server_host}:{args.server_port}/{args.protocol.upper()}->{client_ip}:{client_port}.\033[0m")
            if verbose > 0: print(f"Round-trip time of the message: {calcular_diferenca_timestamp(message["timestamp_send"], timestamp_response)} ms")
            response_data = response.decode()
            if verbose > 2: print(f"+ Server response: {response_data}")
            message = json.loads(response_data)
            message["timestamp_recv"] = timestamp_response
            message["server_response"] = True
            message["client_ip"] = client_ip

        # TODO - enviar essas mensagens para a interface gráfica utilizando o objeto json - colocar um campo observação ou algo do gênero - caso contrário a interface gráfica pode quebrar, já que ela espera o json.
        except socket.timeout:
            if verbose > 0 : print(f"\033[31m\t- No response from {args.server_host}:{args.server_port}/{args.protocol.upper()}.\033[0m")
    


    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)

    if verbose > 0: print(f"Writing to file: {json.dumps(message, indent=4)}")

except (socket.gaierror, socket.herror, socket.timeout, ConnectionResetError, OSError) as e:
    if verbose > 0: print(f"Communication error: {e}")
    # TODO - se o firewall barrar, está dando que é erro! mas foi o firewall, tinha que ver se há como identificar quando é erro e quando é o firewall, por agora vai ficar o status em 0
    #message["status"] = '1'
    #message["status_msg"] = "Network Error"
    message["status"] = '0'
    message["status_msg"] = "Firewall Drop or Network Error"
    dados["tests"].append(message)
    with open(filename, "w") as file:
        json.dump(dados, file, indent=4)
    if verbose > 0: print(f"Writing to file: {json.dumps(message, indent=4)}")

finally:
    if client_sock:
        client_sock.close()

# print que manda a msg para a interface
print(json.dumps(message, indent=4))
