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
from datetime import datetime
import subprocess
import re

total_udp_msgs = 0
total_tcp_msgs = 0
server_ips = []
server_name = "noName"

# Lock registry per log file path to avoid concurrent write corruption
_log_locks = {}
_log_locks_mutex = threading.Lock()

def get_log_lock(filepath):
    """Returns (or creates) a per-file lock for safe concurrent writes."""
    with _log_locks_mutex:
        if filepath not in _log_locks:
            _log_locks[filepath] = threading.Lock()
        return _log_locks[filepath]

def log_received_packet(json_data, server_ip, server_port, protocol):
    """
    Appends a received-packet entry to the server_log.json for this test session.
    The log directory is derived from the timestamp_teste field inside the client JSON,
    so it mirrors the client's log/  structure.

    Args:
        json_data:   Parsed JSON dict sent by the client.
        server_ip:   The server-side IP that accepted the connection.
        server_port: The server-side port that accepted the connection.
        protocol:    'tcp' or 'udp'
    """
    timestamp_teste = json_data.get("timestamp_teste", "unknown")
    dir_name = f"log/{timestamp_teste}"
    os.makedirs(dir_name, exist_ok=True)
    filepath = f"{dir_name}/server_log.json"

    entry = {
        "id":                 json_data.get("id", -1),
        "timestamp_teste":    timestamp_teste,
        "timestamp_received": datetime.now().isoformat(),
        "client_ip":          json_data.get("client_ip", ""),
        "client_port":        json_data.get("client_port", -1),
        "server_ip":          server_ip,
        "server_port":        server_port,
        "protocol":           protocol.upper(),
        "packet_arrived":     True,       # always True – this entry only exists if the packet arrived
    }

    lock = get_log_lock(filepath)
    with lock:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log_data = {"received": []}

        log_data["received"].append(entry)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=4)

    print(f"[LOG] Packet logged -> {filepath}")


def _append_to_log_file(filepath, entry):
    lock = get_log_lock(filepath)
    with lock:
        try:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                log_data = {"received": []}

            log_data.setdefault("received", [])
            log_data["received"].append(entry)

            tmp_filepath = f"{filepath}.tmp"
            with open(tmp_filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=4)
            try:
                os.replace(tmp_filepath, filepath)
            except Exception:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=4)

        except Exception as e:
            try:
                import traceback
                tb = traceback.format_exc()
            except Exception:
                tb = str(e)
            print(f"[LOG-ERROR] Failed to append to {filepath}: {e}\n{tb}")


def _start_tcpdump_monitor():
    """Start a background thread that runs tcpdump and logs SYN attempts."""
    def monitor():
        tcpdump_cmd = [
            "tcpdump", "-l", "-nn", "-i", "any", "tcp and (tcp[13] & 0x12 = 0x02)" # checks only TCP SYN
        ]
        try:
            proc = subprocess.Popen(tcpdump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        except FileNotFoundError:
            print("[SYN-MONITOR] tcpdump not found; SYN monitor disabled.")
            return
        except PermissionError:
            print("[SYN-MONITOR] Permission denied running tcpdump; run as root or grant CAP_NET_RAW.")
            return

        ip_line_re = re.compile(
            r"(?P<time>\d+:\d+:\d+\.\d+)\s+\S+\s+(?:In|Out|in|out)\s+(?:IP|IP6|IP6?)\s+"
            r"(?P<src>[\d.:a-fA-F]+)\.(?P<srcp>\d+)\s+>\s+(?P<dst>[\d.:a-fA-F]+)\.(?P<dstp>\d+):\s+"
            r"Flags\s+\[(?P<flags>[^\]]+)\]"
        )

        syn_log_dir = "log"
        os.makedirs(syn_log_dir, exist_ok=True)
        syn_log_path = os.path.join(syn_log_dir, "syn_log.json")

        print("[SYN-MONITOR] tcpdump monitor started")

        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            m = ip_line_re.search(line)
            if not m:
                continue

            src = m.group('src')
            srcp = int(m.group('srcp'))
            dst = m.group('dst')
            dstp = int(m.group('dstp'))

            entry = {
                "timestamp": datetime.now().isoformat(),
                "client_ip": src,
                "client_port": srcp,
                "server_ip": dst,
                "server_port": dstp,
                "protocol": "TCP",
                "note": "SYN seen (handshake incomplete or in-progress)"
            }
            _append_to_log_file(syn_log_path, entry)
            print(f"[SYN-MONITOR] {src}:{srcp} -> {dst}:{dstp} (SYN)")

        try:
            proc.stdout.close()
            proc.stderr.close()
            proc.kill()
        except Exception:
            pass

    t = threading.Thread(target=monitor, daemon=True, name="tcpdump-monitor")
    t.start()

def get_ips():
    """
        Get IPs from the hosts who execute this code.

        :return: List of IPs from this host.
    """
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family in (2, 10):  # 2 = IPv4, 10 = IPv6
                ip_obj = ipaddress.ip_address(addr.address)  # Converts to IP object.
                if not ip_obj.is_loopback:  # Excludes localhost IPv4 (127.0.0.0/8) and IPv6 (::1)
                    server_ips.append(addr.address)
    
    return server_ips


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
        return False  # Returns False if the IP address is invalid.

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

def lead_with_client_TCP(client_socket):
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
         # Log the received packet immediately
        log_received_packet(json_data, server_ip, server_port, "tcp")
       
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
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except OSError:
        pass
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
        server_ip = server_ips[0] if server_ips else "0.0.0.0"

        # Log the received packet immediately
        log_received_packet(json_data, server_ip, port, "udp")

        if (dest_ip not in server_ips) and check_if_validIP_not_localhost_or_zero(dest_ip):
            print(f"The IP is not in the server list and is not loopback - {dest_ip}")
            #print("different ips")
            host_name = socket.getfqdn()
            server_ip = server_ips[0]
            json_data["message"] = f"Looks like DNAT was made {json_data['server_ip']}->{host_name}"
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
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass
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
    global server_name, server_ips
    server_name = socket.getfqdn() # dont remove, not used in main method, but is used is another methods.
    print(socket.getfqdn())
    server_ips = get_ips() # dont remove, not used in main method, but is used is another methods.
    # start tcpdump-based SYN monitor (logs SYN attempts to log/syn_log.json)
    try:
        _start_tcpdump_monitor()
    except Exception as e:
        print(f"[SYN-MONITOR] failed to start: {e}")
    host = '0.0.0.0'  # Server IP address (localhost)
    #ports = [5000, 5001]  # Ports for the server
    threads = []
    ports_file = "conf/ports.conf"
    tuples = read_ports_from_file(ports_file)
    tuples = list(set(tuples)) # removing duplicates
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
