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
        print("Erro ao executar o comando Docker:", e)
        return []

def run_client_test(containerId):
    """Executa o comando ."""
    try:
        result = subprocess.run(
            ["docker", "exec", containerId, "/firewallTester/src/cliente.py", "192.168.122.200", "tcp", "33", "1", "2025", "0"],
            capture_output=True, text=True, check=True
        )
        #return json.loads(result.stdout)
        print(f"Retornou código {result.returncode}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar o comando Docker:", e)
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


def get_container_info_by_hostname(filter_string):
    """Obtém informações detalhadas dos contêineres Docker cujo hostname contém a string fornecida."""
    print(f"\nObtendo informações do container: \n\tTodos os containers devem ter o contendo a palavra {filter_string}.")
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

                interfaces = {}
                for net_name, net_data in networks.items():
                    interfaces[net_name] = {
                        "IPAddress": net_data["IPAddress"],
                        "MacAddress": net_data["MacAddress"]
                    }

                if filter_string in hostname:
                    matched_containers.append({
                        "id": container_id,
                        "hostname": hostname,
                        "name": name,
                        "interfaces": interfaces
                    })

        return matched_containers

    except subprocess.CalledProcessError as e:
        print("Erro ao executar o comando Docker:", e)
        return []

# TODO - fazer método para retornar hostname, interface, IP

def getContainersHostNames():

    hosts = []

    filter_string = ".test" # parte do nome do container - neste caso todos os containers do teste devem ter em seu nome .test
    matching_containers = get_container_info_by_hostname(filter_string)
    printContainerList(matching_containers)

    print(f"\nObtendo informações de rede do container: \n\tGerando Json dessas informações!.")
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

def printContainerList(matching_containers):
    if matching_containers:
        print(json.dumps(matching_containers, indent=4))
    else:
        print("Nenhum contêiner encontrado com hostname contendo:", filter_string)

# Exemplo de uso
#hosts = getContainersHostNames()
#hosts_json = json.dumps(hosts, indent=2)
#print(hosts_json)
