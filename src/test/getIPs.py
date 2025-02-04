#!/usr/bin/python

import json
import os
import re

# Caminho para o diretório do projeto GNS3
GNS3_PROJECT_PATH = "/home/luiz/GNS3/projects/128cf9a6-7e2d-4b57-9a48-05f9d05ee715/"

# Caminho para o arquivo de topologia
PROJECT_FILE = os.path.join(GNS3_PROJECT_PATH, "novo1.gns3")

# Caminho para a pasta de configurações dos dispositivos
CONFIGS_PATH = os.path.join(GNS3_PROJECT_PATH, "configs")

def extract_ips_from_config():
    """Lê arquivos da pasta configs/ e extrai IPs atribuídos estaticamente."""
    ip_addresses = {}
    if not os.path.exists(CONFIGS_PATH):
        return ip_addresses
    
    for root, _, files in os.walk(CONFIGS_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # Regex para encontrar IPs em configurações de rede
                matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}/?\d*\b', content)
                if matches:
                    ip_addresses[file] = matches
    return ip_addresses

def extract_topology_info():
    """Extrai informações dos nós e interfaces da topologia do GNS3."""
    with open(PROJECT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    nodes_info = []
    for node in data.get("topology", {}).get("nodes", []):
        node_name = node.get("name", "Unknown")
        interfaces = node.get("ports", [])
        interface_info = [{"name": port["name"], "mac": port.get("mac_address", "N/A")} for port in interfaces]
        nodes_info.append({"name": node_name, "interfaces": interface_info})

    return nodes_info

def main():
    print("🔍 Extraindo informações da topologia...")
    topology_info = extract_topology_info()

    print("\n🔍 Buscando IPs em arquivos de configuração...")
    config_ips = extract_ips_from_config()

    print("\n📋 Resultado:")
    for node in topology_info:
        print(f"\nDispositivo: {node['name']}")
        for intf in node["interfaces"]:
            print(f"  - Interface: {intf['name']} | MAC: {intf['mac']}")
        if node["name"] in config_ips:
            print(f"  - IPs Estáticos: {', '.join(config_ips[node['name']])}")

if __name__ == "__main__":
    main()

