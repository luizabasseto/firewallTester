#!/usr/local/bin/python

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
    Program Name: Firewall Tester - Server
    Description: Acts as a server on multiple ports so that firewall rule testing software can receive packets in the test scenario.
    Author: Luiz Arthur Feitosa dos Santos - luiz.arthur.feitosa.santos@gmail.com / luizsantos@utfpr.edu.br
    License: GNU General Public License v3.0
    Version: 1.0
"""

import socket
import json
import threading
import psutil
import ipaddress
import os
import signal
import time

total_udp_msgs = 0
total_tcp_msgs = 0
server_ips = []
server_name = "noName"

def get_ips():
    """
        Get IPs from the hosts who execute this code.

        :return: List of IPs from this host.
    """
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family in (2, 10):  # 2 = IPv4, 10 = IPv6
                ip_obj = ipaddress.ip_address(addr.address)  # Converte para objeto IP
                if not ip_obj.is_loopback:  # Exclui localhost IPv4 (127.0.0.0/8) e IPv6 (::1)
                    server_ips.append(addr.address)
    
    return server_ips

# TODO - Test and remove this method.
# def is_not_loopback(ip):
#     return not ipaddress.ip_address(ip).is_loopback

def check_if_validIP_not_localhost_or_zero(ip):
    """
    Checks if an IP address is not 0.0.0.0 o 127.0.0.0/8 (loopback).

    Args:
        ip: Ip to be tested.
    
    :return: False if the address is not valid. True if is a valid IP.
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        loopback_rede = ipaddress.ip_network("127.0.0.0/8")
        return ip_obj != ipaddress.ip_address("0.0.0.0") and ip_obj not in loopback_rede
    except ValueError:
        return False  # Retorna False se o endereço IP for inválido

def add_dnat_to_json(object_json, host_name, ip, port):
    """
        Adds the 'dnat' field to the JSON object.

        Args:
            object_json: json object to be changed.
            host_name: Hostname from this server.
            ip: IP from this server.
            port: Network port from this server.

        :return: Json object with DNAT fiedls.
    """

    object_json["dnat"] = {
        "host_name": host_name,
        "ip": ip,
        "port": port,
    }
    return object_json


def read_ports_from_file(file_name):
    """
    Reads a file with port/protocol tuples (one per line) and returns a list of tuples.

        Args:
            file_name (str): The name of the file to be read.

        Returns: A list of tuples (port, protocol) or None on error.
    """
    try:
        with open(file_name, 'r') as file:
            content = file.readlines()

        tuples = []
        for line in content:
            line = line.strip()  # Remove extra spaces
            if line: # Checks if the line is not empty
                try:
                    port_and_protocol = line.split('/')
                    if len(port_and_protocol) == 2:
                        port = int(port_and_protocol[0])
                        protocol = port_and_protocol[1].lower() # Convert to lowercase for consistency
                        tuples.append((port, protocol))
                    else:
                        print(f"Error: Invalid line: '{line}'. Format must be port/protocol.")

                except ValueError:
                    print(f"Error: Invalid port in line: '{line}'. Must be an integer.")

        return tuples

    except FileNotFoundError:
        print(f"Error: File  '{file_name}' not found.")
        return None

def get_pid_by_port(protocol, port):
    """
        Returns the PID of the process using the specified port.

        Args:
            protocol: Protocol (TCP/UDP)
            port: Network port
        
        :return: PID - Process ID
    """
    print(f"Get process pid on port {port}.")
    for conn in psutil.net_connections(kind=protocol):
        if conn.laddr.port == port:
            return conn.pid
    return None

def kill_pid_by_port(protocol, port):
    """
        Kill a process running on a port via pid

        Args:
            protocol: Protocol (TCP/UDP).
            port: Network port.
    """
    print(f"Kill process on port {port}.")
    pid = get_pid_by_port(protocol, port)
    if  pid != None:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Process {pid} successfully terminated.")

        except Exception as e:
            print(f"Error terminating process {pid}: {e}")

def show_total_msgs():
    """
        Shows the total number of messages sent by clients and processed by the server in this program.
    """
    global total_tcp_msgs, total_udp_msgs
    print(f"Number of messages:\n\t * TCP: {total_tcp_msgs};\n\t * UDP: {total_udp_msgs};\n\t * Total: {total_tcp_msgs+total_udp_msgs};")

# TODO - alterar o objeto json enviado pelo cliente, caso a mensagem esteja com um IP diferente do host de destino, isso significa que a mensagem passou por um nat, então seria legal colocar o IP/porta do host que recebeu e tratou a informação para informar que o DNAT foi bem sucessido ou não - isso tem que ser feito para tcp e udp.
def lidar_com_cliente_TCP(client_socket):
    """
        Deals with communication with a client.

        Args:
            client_socket: Client Socket.
    """
    global total_tcp_msgs
    try:
        data = client_socket.recv(1024).decode('utf-8')
        total_tcp_msgs += 1
        json_data = json.loads(data)
        print(f"Received JSON object:\n", json.dumps(json_data, indent=4))

        dest_ip = json_data["server_ip"]

        server_address = client_socket.getsockname()
        server_ip, server_port = server_address
        #server_ips.append("0.0.0.0")
        #if (dest_ip not in server_ips) and is_not_loopback(dest_ip): ip_valido_nao_loopback_nem_zero
        if (dest_ip not in server_ips) and check_if_validIP_not_localhost_or_zero(dest_ip):
            #print(f"ips diferentes {dest_ip}")
            host_name = socket.getfqdn()
            json_data["message"] = f"Looks like DNAT was made {json_data['server_ip']}->{host_name}"
            json_data = add_dnat_to_json(json_data, host_name, server_ip, server_port)
            print(json.dumps(json_data, indent=4))

        client_socket.send(json.dumps(json_data).encode('utf-8'))

    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Error decoding received JSON object or invalid data.")
        client_socket.send("Error: Invalid JSON object or invalid data.".encode('utf-8'))

    finally:
        client_socket.close()
        print("Connection with client closed.")
        show_total_msgs()

def server_udp(port):
    """
        Start UDP server.

        Args:
            port: UDP port where the server will run. 
    """
    global total_udp_msgs
    host = '0.0.0.0'
    protocol = 'udp'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))  # Bind to local address and port

    while True:
        data, addr = sock.recvfrom(1024)  # Receives 1024 bytes of data
        total_udp_msgs += 1
        print(f"Message received from {addr}: {data.decode()}")

        # Send an optional response
        response = f"Received: {data.decode()}"
        message_json = data.decode('utf-8')
        json_data = json.loads(message_json)
        
        dest_ip = json_data["server_ip"]
        #if (dest_ip not in server_ips) and is_not_loopback(dest_ip):
        if (dest_ip not in server_ips) and check_if_validIP_not_localhost_or_zero(dest_ip):
            print(f"The IP is not in the server list and is not loopback - {dest_ip}")
            #print("different ips")
            host_name = socket.getfqdn()
            server_ip = server_ips[0]
            # TODO - the server IP may be presented strangely here, as we are taking the first IP of the server host, and in the rule it may have been redirected to another IP of the same server.
            json_data["message"] = f"Looks like DNAT was made {json_data["server_ip"]}->{host_name}"
            json_data = add_dnat_to_json(json_data, host_name, server_ip, port)
            print(json.dumps(json_data, indent=4))
        
        response = json.dumps(json_data).encode('utf-8')
        sock.sendto(response, addr)
        show_total_msgs()

def start_server(host, protocol, port):
    """
        Starts a TCP or UDP server on a specific port.

        Args:
            host: Host;
            protocol: protocol (TCP/UDP);
            port: Network port.
    """
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
            client_thread = threading.Thread(target=server_udp, args=(port,))
            client_thread.start()

    else:
        print(f">>> WARNING!!! Could not start this port: {protocol}/{port}")


def main():
    """
        Main method.
    """
    server_name = socket.getfqdn() # dont remove, not used in main method, but is used is another methods.
    print(socket.getfqdn())
    server_ips = get_ips() # dont remove, not used in main method, but is used is another methods.
    host = '0.0.0.0'  # Server IP address (localhost)
    #ports = [5000, 5001]  # Ports for the server
    threads = []
    ports_file = "conf/ports.conf"
    tuples = read_ports_from_file(ports_file)
    print(f"Starting servers with ports present in file: {ports_file} - This file must contain lines with port/protocol, example 80/tcp.")
    if tuples:
        print("Tuples read from file:")
        for port, protocol in tuples:
            if protocol == "tcp" or protocol == "udp":
                print(f"Starting {port}/{protocol}")
                kill_pid_by_port(protocol, port)
                thread = threading.Thread(target=start_server, args=(host, protocol, port), daemon=True)
                threads.append(thread)
                thread.start()
            else:
                print(f"Protocol not supported: {protocol}")
    else:
        print(f"Could not read ports and protocols from file {ports_file}.")

    time.sleep(3)
    print("\nIf needed, press Ctrl+C to terminate the program.")
    try:
        while True:
            time.sleep(1)  # Keeps the main program running
    except KeyboardInterrupt:
        print("\nProgram terminated with Ctrl+C.")

if __name__ == "__main__":
    main()
