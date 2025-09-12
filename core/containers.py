#!/usr/bin/python


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
    Program Name: Firewall Tester - Containers
    Description: Performs communication between the firewall rule testing software interface and Dockers containers.
    Author: Luiz Arthur Feitosa dos Santos - luiz.arthur.feitosa.santos@gmail.com / luizsantos@utfpr.edu.br
    License: GNU General Public License v3.0
    Version: 1.0
"""

import subprocess
import json
from .docker_host import DockerHost

def get_ip_info_from_docker(container_id):
    """
    Runs the command 'ip -4 -json a' inside a Docker container and returns the resulting JSON.
    
    Args:
        containerId: container ID.
    
    :return: 
        A list of containers informations.
    """
    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "ip", "-4", "-json", "a"],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return []

def start_server(container_id):
    """
        Starts the script that simulates server ports in containers.
        
        Args:
            containerId: container ID - container that will start the server.
    """
    # TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! See how to solve...
    print(f"Start server in container {container_id}")
    try:
        result = subprocess.run(
            # docker exec -d 9a0a52c42ea8 ./server.py
            ["docker", "exec", "-d", container_id, "./server.py"],
            capture_output=True, text=True, check=True
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError: # actually the output for the command's success doesn't return anything, so it gives the json error.
            print("Servers turned on...")
            print("Output received:", result.stdout)
            return None  # Or some default value

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return []

def stop_server(container_id):
    """
        Stop the script that simulates server ports in containers.
        
        Args:
            containerId: container ID - container that will stop the server.
    """
    print(f"Stop server in container {container_id}")
    command = 'docker exec '+ container_id +' pkill server.py'
    run_command_shell(command)
    
def run_command(command):
    """
        Execute a command.
        
        Args:
            command: command that will be executed, but the commands, their options and parameters must be in a python list.
    """
    # TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! see how to solve...
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return e

# para executar sem precisar separar em lista
def run_command_shell(command):
    """
        Execute a command but the commando is like the console command, not a list.
        
        Args:
            command: command that will be executed.
    """
    # TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! see how to solve...
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print("Error executing Docker command:", e)
        return None



def get_port_from_container(container_id):
    """
        Get open ports from container:

        Args:
            container_id: ID from container.
    """
    print(f"Get ports from container - {container_id}")

    net_command = ' netstat -atuln | awk \'$1 ~ /^(tcp|udp)$/ {split($4, a, ":"); print $1 "/" a[2]}\' | sort -t \'/\' -k 2n'
    command = "docker exec "+container_id+net_command
    
    #docker exec 9eb8ef3327d1 netstat -atuln | awk '$1 ~ /^(tcp|udp)$/ {split($4, a, ":"); print $1 "/" a[2]}' | sort -t '/' -k 2n

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        # Processes output to get protocol and port
        ports = []
        for linha in result.stdout.splitlines():
            if '/' in linha:
                protocol, port = linha.split('/')
                ports.append((protocol.upper(), int(port)))  # Add to list as tuple
        return ports
    else:
        print(f"Error: {result.stderr}")
        return []  # Returns an empty list on error
    
def copy_host2container(container_id, source_file, destination_file):
    """
        Copy a file from host to container.

        Args:
            container_id: Container ID.
            source_file: Source file.
            destination_file: Destination file.

    """
    print(f"Copy file ({source_file}) to container {container_id}")
    command = "docker cp "+source_file+" "+ container_id+":"+destination_file
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        print("Copy successfully completed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("Error executing Docker copy: ", e)
        return 1

def copy_ports2server(container_id, source_file):
    """
        Copy ports file to container/server.
        
        Args:
            container_id: Container ID.
            source_file: Source file.
    """
    print(f"Copy port file to server in container {container_id}")
    return copy_host2container(container_id, source_file, "/firewallTester/src/conf/ports.conf")

#teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port
def run_client_test(container_id, dst_ip, protocol, dst_port, teste_id, timestamp, verbose):
    """
        Executa o teste no container/host.

        Args:
            container_id: Container ID;
            dst_ip: Destination IP;
            protocol: Protocol (TCP, UDP or ICMP);
            dst_port: Destination port;
            test_id: Test ID - some value;
            timestamp: Timestamp from test.
            verbose: Output verbose - the Firewall test interface just suport verbose mode 0 - DONT USE ANOTHER VALUE.
    """
    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "/firewallTester/src/client.py", dst_ip, protocol, dst_port, teste_id, "2025", "0"],
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
    """
        Processes the JSON output of the 'ip -4 -json a' command and displays network interfaces and their IPs, ignoring interface 'lo' (loopback).

        Args:
            interfaces: network interfaces from a host;
            host: A host.
    """

    for interface in interfaces:
        list=[]
        if interface["ifname"] == "lo":
            continue  # Ignore the loopback interface

        ifname = interface["ifname"]
        ips = [addr["local"] for addr in interface.get("addr_info", [])]

        if ips:
            #print(f"\tInterface: {ifname}")
            for ip in ips:
                #print(f"\t\t  IP: {ip}")
                list.append(ip)

        host.add_interface(interface["ifname"], list)

    return host

def extract_hostname_ips(json_list):
    """
        Extrai o hostname e os IPs de uma lista de objetos JSON.

        Args:
            param: json_list: List of JSON objects in DockerHost format.
            
        :return: List of strings in the format "hostname: ip".
    """
    result = []

    # Iterates through each JSON object in the list
    for host in json_list:
        hostname = host["hostname"]

        # Iterates through each network interface
        for interface in host["interfaces"]:
            # Iterates through IP interface
            for ip in interface["ips"]:
                result.append(f"{hostname}: {ip}")

    return result

def extract_containerid_hostname_ips( ):
    """
    Extracts the container ID, hostname and IPs from a list of JSON objects.
    
    :return: Sorted list of dictionaries in the format {"id": "container_id", "hostname": "hostname", "ip": "ip"}.
    """

    json_list = getContainersByImageName()  # get container information (id, hostname, etc)

    result = []

    # Iterates through each JSON object in the list
    for host in json_list:
        hostname = host["hostname"]
        container_id = host["id"]
        #print(f"{hostname} - {host["interfaces"]}")

        if not host["interfaces"]:     # Checks for IPs on the interface
                result.append({
                    "id": container_id,
                    "hostname": hostname,
                    "ip": "0.0.0.0"
                })
        else:
            # Iterates through each network interface
            for interface in host["interfaces"]:
                # Iterates through IP interface
                for ip in interface["ips"]:
                    # Adds a dictionary with container information
                    result.append({
                        "id": container_id,
                        "hostname": hostname,
                        "ip": ip
                    })

    return sorted(result, key=lambda x: x["hostname"])

def get_containerid_hostname( ):
    """
    Get the container ID and hostname.
    
    :return: Sorted list of dictionaries in the format [container_id, hostname}.
    """

    json_list = getContainersByImageName()  # get container information (id, hostname, etc)

    result = []

    # Iterates through each JSON object in the list
    for host in json_list:
        hostname = host["hostname"]
        container_id = host["id"]
        result.append([container_id, hostname])
    return sorted(result, key=lambda x: x[1])


def extract_hostname_interface_ips(json_list):
    """
    Extracts the hostname and network interfaces with their IPs from a list of JSON objects.

    Args:
        json_list: List of JSON objects in DockerHost format.
    
    :return: List of lists in the format [hostname, [interface1, interface2, ...]],
        where each interface is a dictionary {"name": "eth0", "ips": ["ip1", "ip2"]}.
    """
    print(f"\nGetting list: hostname and interfaces:ip.")
    result = []

    # Iterates through each JSON object in the list
    for host in json_list:
        hostname = host["hostname"]
        interfaces = []

        # Iterates through each network interface
        for interface in host["interfaces"]:
            interface_name = interface["nome"]
            ips = interface["ips"]

            # Adds the interface as a dictionary to the interface list
            interfaces.append({"nome": interface_name, "ips": ips})

        # Adds the hostname and interface list to the output
        result.append([hostname, interfaces])
    #print(f"result: {result}")
    return result

def get_container_info_by_filter(filter_string):
    """
        Gets detailed information about Docker containers whose hostname contains the given string.
        
        Args:
            filter_string: String filter that will be used in the container search.
        
        :return: List of containers that match with the filter.
    """
    print(f"\nGetting container information: \n\tAll containers must have names containing the word: {filter_string}.")
    try:
        # Get all running containers
        result = subprocess.run(
            ["docker", "ps", "-q"], capture_output=True, text=True, check=True
        )
        container_ids = result.stdout.strip().split("\n")

        matched_containers = []

        for container_id in container_ids:
            if not container_id:
                continue

            # Get container details
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

                # TODO - here I changed it so that the search is by the name of the image on DockerHub, which is firewall_tester - that is, the search is by the image and not by the host name - but this has a problem if docker is not used, but here it would only be possible to use docker!
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

# TODO - make method to return hostname, interface, IP

def getContainersByImageName():
    """
        Get containers using Docker image name. Previously this was returned by the host name, but this was changed to the image name.
        
        :return: A list of containers/hosts.
    """

    hosts = []
    filter_string = "firewall_tester" # part of the image name - in this case all test containers must have firewall_tester in their iamge name
    matching_containers = get_container_info_by_filter(filter_string)
    #printContainerList(matching_containers, filter_string)

    print(f"\nGetting container network information: \n\tGenerating JSON of this information!")
    for container in matching_containers:

        host = DockerHost(
            container_id=container['id'],
            nome=container['name'],
            hostname=container['hostname']
        )

        #print(f"\nContainer found: {container['hostname']} - ID: {container['id']}")
        # Run the command in Docker and process the output
        interfaces = get_ip_info_from_docker(container['id'])
        #print(f"interfaces - {interfaces}")
        host = process_ip_info(interfaces, host)
        #print(f"IPs - {ipContainer}")
        #lista.extend(ipContainer)

        hosts.append(host.to_dict())

    hosts_json = json.dumps(hosts, indent=2)
    #print(hosts_json)
    return hosts

def printContainerList(matching_containers, filter_string):
    if matching_containers:
        print(json.dumps(matching_containers, indent=4))
    else:
        print("No container found with hostname containing:", filter_string)

# Example of use
#hosts = getContainersHostNames()
#hosts_json = json.dumps(hosts, indent=2)
#print(hosts_json)
