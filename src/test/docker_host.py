#!/usr/bin/python

import json

class DockerHost:
    def __init__(self, container_id, nome, hostname):
        """
        Inicializa um objeto DockerHost.

        :param container_id: ID do container Docker.
        :param nome: Nome do container.
        :param hostname: Hostname do container.
        """
        self.container_id = container_id
        self.nome = nome
        self.hostname = hostname
        self.interfaces = []

    def add_interface(self, interface_name, ips=None):
        """
        Adiciona uma nova interface de rede ao container.

        :param interface_name: Nome da interface (ex: eth0).
        :param ips: Lista de endereços IPs da interface (opcional).
        """
        if ips is None:
            ips = []
        interface = {
            "nome": interface_name,
            "ips": ips
        }
        self.interfaces.append(interface)

    def extract_hostname_ips(self, lista_json):
        """
        Extrai o hostname e os IPs de uma lista de objetos JSON.

        :param lista_json: Lista de objetos JSON no formato DockerHost.
        :return: Lista de strings no formato "hostname: ip".
        """
        resultado = []

        # Percorre cada objeto JSON na lista
        for host in lista_json:
            hostname = host["hostname"].replace(".teste", "")

            # Percorre cada interface de rede
            for interface in host["interfaces"]:
                # Percorre cada IP da interface
                for ip in interface["ips"]:
                    resultado.append(f"{hostname}: {ip}")

        return resultado

    def add_ip_to_interface(self, interface_name, ip):
        """
        Adiciona um IP a uma interface de rede existente.

        :param interface_name: Nome da interface (ex: eth0).
        :param ip: Endereço IP a ser adicionado.
        """
        for interface in self.interfaces:
            if interface["nome"] == interface_name:
                interface["ips"].append(ip)
                return
        raise ValueError(f"Interface '{interface_name}' não encontrada.")

    def to_dict(self):
        """
        Converte o objeto para um dicionário.

        :return: Dicionário representando o objeto DockerHost.
        """
        return {
            "id": self.container_id,
            "nome": self.nome,
            "hostname": self.hostname,
            "interfaces": self.interfaces
        }

    def to_json(self, indent=2):
        """
        Converte o objeto para uma string JSON.

        :param indent: Nível de indentação do JSON (opcional).
        :return: String JSON representando o objeto DockerHost.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def __str__(self):
        """
        Retorna uma representação legível do objeto como JSON.

        :return: String JSON formatada.
        """
        return self.to_json()
