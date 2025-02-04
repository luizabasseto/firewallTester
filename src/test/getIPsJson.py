#!/usr/bin/python

import subprocess
import json

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

def process_ip_info(interfaces):
    """Processa a saída JSON do comando 'ip -4 -json a' e exibe interfaces e seus IPs, ignorando 'lo'."""
    for interface in interfaces:
        if interface["ifname"] == "lo":
            continue  # Ignora a interface de loopback

        ifname = interface["ifname"]
        ips = [addr["local"] for addr in interface.get("addr_info", [])]

        if ips:
            print(f"Interface: {ifname}")
            for ip in ips:
                print(f"  IP: {ip}")

# Executa o comando no Docker e processa a saída
interfaces = get_ip_info_from_docker("732f4a83c02c")
process_ip_info(interfaces)
