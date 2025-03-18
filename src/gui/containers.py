#!/usr/bin/python

import subprocess
import json
from docker_host import DockerHost

def get_ip_info_from_docker(containerId):
    """Executa o comando 'ip -4 -json a' dentro de um contêiner Docker e retorna o JSON resultante."""
    try:
        result = subprocess.run(
            ["docker", "exec", containerId, "ip", "-4", "-json", "a"],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return []

def start_server(containerId):
    """Inicia o script de que simula portas servidoras nos containers -."""
    # TODO - se tiver utilizando DHCP as portas 68 e 69 UDP podem estar em uso, ai não dá para executar essas portas! ver como resolver...
    print(f"Start server in container {containerId}")
    try:
        result = subprocess.run(
            # docker exec -d 9a0a52c42ea8 ./server.py
            ["docker", "exec", "-d", containerId, "./server.py"],
            capture_output=True, text=True, check=True
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError: # na verdade a saída para sucesso do comando não retorna nada, então ele dá o erro do json
            print("Servers turned on...")
            print("Output received:", result.stdout)
            return None  # Ou algum valor padrão

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return []

def stop_server(containerId):
    print(f"Stop server in container {containerId}")
    command = 'docker exec '+ containerId +' pkill server.py'
    run_command_shell(command)
    
def run_command(command):
    """Inicia o script de que simula portas servidoras nos containers -."""
    # TODO - se tiver utilizando DHCP as portas 68 e 69 UDP podem estar em uso, ai não dá para executar essas portas! ver como resolver...
    #print(f"Executa comando {command}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return e

# para executar sem precisar separar em lista
def run_command_shell(command):
    """Inicia o script de que simula portas servidoras nos containers -."""
    # TODO - se tiver utilizando DHCP as portas 68 e 69 UDP podem estar em uso, ai não dá para executar essas portas! ver como resolver...
    #print(f"Executa comando {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return None



def get_port_from_container(containerId):
    print(f"Get ports from container - {containerId}")

    comandoNet = ' netstat -atuln | awk \'$1 ~ /^(tcp|udp)$/ {split($4, a, ":"); print $1 "/" a[2]}\' | sort -t \'/\' -k 2n'
    comando = "docker exec "+containerId+comandoNet
    
    #docker exec 9eb8ef3327d1 netstat -atuln | awk '$1 ~ /^(tcp|udp)$/ {split($4, a, ":"); print $1 "/" a[2]}' | sort -t '/' -k 2n

    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    if resultado.returncode == 0:
        # Processa a saída para obter protocolo e porta
        portas = []
        for linha in resultado.stdout.splitlines():
            if '/' in linha:
                protocolo, porta = linha.split('/')
                portas.append((protocolo.upper(), int(porta)))  # Adiciona à lista como tupla
        return portas
    else:
        print(f"Error: {resultado.stderr}")
        return []  # Retorna uma lista vazia em caso de erro
    
def copy_host2container(containerId, fileSrc, fileDest):
    print(f"Copy file ({fileSrc}) to container {containerId}")
    comando = "docker cp "+fileSrc+" "+ containerId+":"+fileDest
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        print(result.stdout)
        print("Copy successfully completed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("Error executing Docker copy: ", e)
        return 1

def copy_ports2server(containerId, fileSrc):
    print(f"Copy port file to server in container {containerId}")
    return copy_host2container(containerId, fileSrc, "/firewallTester/src/conf/portas.conf")

#teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port
def run_client_test(containerId, dst_ip, protocol, dst_port, teste_id, timestamp, verbose):
    """Executa o comando tem que passar Id do container, IP de destino, protocol, porta de destino, id do teste, timestamp, verbose"""
    try:
        result = subprocess.run(
            ["docker", "exec", containerId, "/firewallTester/src/cliente.py", dst_ip, protocol, dst_port, teste_id, "2025", "0"],
            capture_output=True, text=True, check=True
        )
        #return json.loads(result.stdout)
        print(f"Returned code {result.returncode}")
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return []

def process_ip_info(interfaces, host):
    """Processa a saída JSON do comando 'ip -4 -json a' e exibe interfaces e seus IPs, ignorando 'lo'."""

    for interface in interfaces:
        lista=[]
        if interface["ifname"] == "lo":
            continue  # Ignora a interface de loopback

        ifname = interface["ifname"]
        ips = [addr["local"] for addr in interface.get("addr_info", [])]

        if ips:
            #print(f"\tInterface: {ifname}")
            for ip in ips:
                #print(f"\t\t  IP: {ip}")
                lista.append(ip)

        host.add_interface(interface["ifname"], lista)

    return host

def extract_hostname_ips(lista_json):
    """
    Extrai o hostname e os IPs de uma lista de objetos JSON.

    :param lista_json: Lista de objetos JSON no formato DockerHost.
    :return: Lista de strings no formato "hostname: ip".
    """
    resultado = []

    # Percorre cada objeto JSON na lista
    for host in lista_json:
        hostname = host["hostname"]

        # Percorre cada interface de rede
        for interface in host["interfaces"]:
            # Percorre cada IP da interface
            for ip in interface["ips"]:
                resultado.append(f"{hostname}: {ip}")

    return resultado

def extract_containerid_hostname_ips( ):
    """
    Extrai o ID do container, hostname e IPs de uma lista de objetos JSON.

    :param lista_json: Lista de objetos JSON no formato DockerHost.
    :return: Lista de dicionários no formato {"id": "container_id", "hostname": "hostname", "ip": "ip"}.
    """

    lista_json = getContainersHostNames()  # obtém as informações dos containers (id, hostname, etc)

    resultado = []

    # Percorre cada objeto JSON na lista
    for host in lista_json:
        hostname = host["hostname"]
        containerid = host["id"]
        #print(f"{hostname} - {host["interfaces"]}")

        if not host["interfaces"]:     # Verifica se há IPs na interface
                resultado.append({
                    "id": containerid,
                    "hostname": hostname,
                    "ip": "0.0.0.0"
                })
        else:
            # Percorre cada interface de rede
            for interface in host["interfaces"]:
                # Percorre cada IP da interface
                for ip in interface["ips"]:
                    # Adiciona um dicionário com as informações do container
                    resultado.append({
                        "id": containerid,
                        "hostname": hostname,
                        "ip": ip
                    })

    return sorted(resultado, key=lambda x: x["hostname"])

def extract_hostname_interface_ips(lista_json):
    """
    Extrai o hostname e as interfaces de rede com seus IPs de uma lista de objetos JSON.

    :param lista_json: Lista de objetos JSON no formato DockerHost.
    :return: Lista de listas no formato [hostname, [interface1, interface2, ...]],
             onde cada interface é um dicionário {"nome": "eth0", "ips": ["ip1", "ip2"]}.
    """
    print(f"\nGetting list: hostname and interfaces:ip.")
    resultado = []

    # Percorre cada objeto JSON na lista
    for host in lista_json:
        hostname = host["hostname"]
        interfaces = []

        # Percorre cada interface de rede
        for interface in host["interfaces"]:
            interface_name = interface["nome"]
            ips = interface["ips"]

            # Adiciona a interface como um dicionário à lista de interfaces
            interfaces.append({"nome": interface_name, "ips": ips})

        # Adiciona o hostname e a lista de interfaces ao resultado
        resultado.append([hostname, interfaces])
    print(f"result: {resultado}")
    return resultado

def get_container_info_by_hostname(filter_string):
    """Obtém informações detalhadas dos contêineres Docker cujo hostname contém a string fornecida."""
    print(f"\nGetting container information: \n\tAll containers must have names containing the word: {filter_string}.")
    try:
        # Obtém todos os contêineres em execução
        result = subprocess.run(
            ["docker", "ps", "-q"], capture_output=True, text=True, check=True
        )
        container_ids = result.stdout.strip().split("\n")

        matched_containers = []

        for container_id in container_ids:
            if not container_id:
                continue

            # Obtém detalhes do contêiner
            inspect_cmd = [
                "docker", "inspect", container_id
            ]
            inspect_result = subprocess.run(inspect_cmd, capture_output=True, text=True)

            if inspect_result.returncode == 0:
                container_data = json.loads(inspect_result.stdout)[0]
                hostname = container_data["Config"]["Hostname"]
                name = container_data["Name"].strip("/")
                networks = container_data["NetworkSettings"]["Networks"]
                image = container_data["Config"]["Image"]

                interfaces = {}
                for net_name, net_data in networks.items():
                    interfaces[net_name] = {
                        "IPAddress": net_data["IPAddress"],
                        "MacAddress": net_data["MacAddress"]
                    }

                # TODO - aqui mudei para que a busca seja pelo nome da imagem no DockerHub, que é firewall_tester - ou seja a busca é pela imagem e não pelo nome do host - mas isso tem um problema caso não for utilizado docker, mas aqui só seria possível utilizar docker mesmo!
                #if filter_string in hostname:
                if filter_string in image:
                    matched_containers.append({
                        "id": container_id,
                        "hostname": hostname,
                        "name": name,
                        "interfaces": interfaces
                    })

        return matched_containers

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return []

# TODO - fazer método para retornar hostname, interface, IP

def getContainersHostNames():

    hosts = []

    filter_string = "firewall_tester" # parte do nome do container - neste caso todos os containers do teste devem ter em seu nome .test
    matching_containers = get_container_info_by_hostname(filter_string)
    printContainerList(matching_containers, filter_string)

    print(f"\nGetting container network information: \n\tGenerating JSON of this information!")
    for container in matching_containers:

        host = DockerHost(
            container_id=container['id'],
            nome=container['name'],
            hostname=container['hostname']
        )

        #print(f"\nContainer localizado: {container['hostname']} - ID: {container['id']}")
        # Executa o comando no Docker e processa a saída
        interfaces = get_ip_info_from_docker(container['id'])
        #print(f"interfaces - {interfaces}")
        host = process_ip_info(interfaces, host)
        #print(f"IPs - {ipContainer}")
        #lista.extend(ipContainer)

        hosts.append(host.to_dict())


    hosts_json = json.dumps(hosts, indent=2)
    print(hosts_json)
    return hosts

def printContainerList(matching_containers, filter_string):
    if matching_containers:
        print(json.dumps(matching_containers, indent=4))
    else:
        print("No container found with hostname containing:", filter_string)

# Exemplo de uso
#hosts = getContainersHostNames()
#hosts_json = json.dumps(hosts, indent=2)
#print(hosts_json)
