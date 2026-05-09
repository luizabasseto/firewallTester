#!/usr/local/bin/python

"""
    Program Name: Firewall Tester - Client
    Description: Acts as a client so that the firewall rule testing software 
    can send packets to the server software in the test scenario.
    Author: Luiz Arthur Feitosa dos Santos - 
    luiz.arthur.feitosa.santos@gmail.com / luizsantos@utfpr.edu.br
    License: GNU General Public License v3.0
    Version: 1.0
"""

import socket
import argparse
import json
import os
import time
import sys
from datetime import datetime

from scapy.all import IP, ICMP, sr1

def validate_host(host):
    """Checks if a hostname can be resolved."""
    try:
        socket.gethostbyname(host)  # Try to resolve the hostname.
        return True  # Valid Host
    except socket.gaierror:
        return False  # Invalid Host

def ping(host, count):
    """It sends ICMP Echo Request packets and checks for the response."""
    received = 0
    # The count is ignored; only one ping is sent per test run.
    count = 1
    if verbose > 0:
        print(f"\nPING {host}:")
    for seq in range(1, count + 1):
        if not validate_host(host):
            return -1 

        packet = IP(dst=host) / ICMP()
        start_time = time.time()

        reply = sr1(packet, timeout=1, verbose=False)  # Send the package and wait for a response.

        if reply:
            elapsed_time = (time.time() - start_time) * 1000
            if verbose > 0:
                print(f"\033[32m\t+ Response from {host}: Time = {elapsed_time:.2f} ms - {seq}/{count}\033[0m")
            received += 1
        else:
            if verbose > 0:
                print(f"\033[31m\t- No response from {host} - {seq}/{count}\033[0m")

        time.sleep(1)
    return received

def calculate_difference_timestamp(timestamp_send, timestamp_received):
    """Calculates the difference between two timestamps in ISO 8601 format in milliseconds."""
    t1 = datetime.fromisoformat(timestamp_send)
    t2 = datetime.fromisoformat(timestamp_received)
    diferenca = (t2 - t1).total_seconds() * 1000  # Convert to milliseconds
    return diferenca

# Configuring command-line arguments
parser = argparse.ArgumentParser(description="Firewall Tester Client (UDP/TCP/ICMP)")
parser.add_argument("server_host", type=str, help="Server IP address")
parser.add_argument("protocol", type=str.lower, help="Protocol used: TCP/UDP/ICMP")
parser.add_argument("server_port", type=int, help="Server Port")
parser.add_argument("testId", type=int, help="Test ID")
parser.add_argument("timestamp", type=str, help="Timestamp of Test")
parser.add_argument("verbose", type=int, help="Level of verbosity (0, 1, 2)")

args = parser.parse_args()
verbose = args.verbose

# Initializing socket according to protocol.
client_sock = None
client_port = -1
icmp_status = 0

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
    client_port = 0  # ICMP does not use conventional ports.
else:
    if verbose > 0: print("Choose a valid protocol (TCP, UDP ou ICMP).")
    sys.exit(1)

# Obtaining customer information
client_host = socket.gethostname()
try:
    client_ip = socket.gethostbyname(client_host)
except socket.gaierror:
    client_ip = "0.0.0.0" # Could not resolve hostname
timestamp = datetime.now().isoformat()

# Creating the directory and naming the JSON file
filename_timestamp = args.timestamp
dir_name = f"log/{filename_timestamp}"
filename = f"{dir_name}/test.json"
os.makedirs(dir_name, exist_ok=True)

# Loading existing JSON or creating a new one.
try:
    with open(filename, 'r', encoding="utf-8") as file:
        dados = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    dados = {"tests": []}

# Creating JSON Structure
# status - this is for cases where something happens, such as the packet not being able to be sent because the client host has no route!

# message - can be used to simulate, for example, sending a malicious message in the application layer, such as using inappropriate words (porn, hacker, etc.) or suspicious terms ("/etc/shadow")
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
# If the status is zero, everything went well; otherwise, an error occurred, such as:
# 1 - Network error

# Treatment for ICMP
if args.protocol == "icmp":
    if icmp_status < 0:
        message["status"] = "0"
        message["status_msg"] = "Firewall Drop or Host desconhecido"
    else:
        message["server_response"] = icmp_status > 0
        message["server_port"] = 8  # ICMP echo reply

    dados["tests"].append(message)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4)
    if verbose > 0:
        print(f"Writing to file: {json.dumps(message, indent=4)}")

    print(json.dumps(message, indent=4))
    sys.exit(0)

# Data transmission (UDP and TCP)
json_message = json.dumps(message, indent=4)
server_address = (args.server_host, args.server_port)

try:
    if verbose > 0: print(f"-> Sending message to: {args.server_host}:{args.server_port}/{args.protocol.upper()}.")
    if verbose > 0:
        print(f"Sending: {json_message}")

    if args.server_host == "0.0.0.0":
        message["status_msg"] = "Error by using destination IP 0.0.0.0"
    else:
        if args.protocol == "udp":
            client_sock.sendto(json_message.encode(), server_address)
        else:  # TCP
            client_sock.connect(server_address)
            client_sock.send(json_message.encode())
            # retrieves the IP address of the client that was actually used in the transmission.
            client_ip = client_sock.getsockname()[0]
        
        try:
            response, _ = client_sock.recvfrom(1024) if args.protocol == "udp" else (client_sock.recv(1024), None)
            timestamp_response = datetime.now().isoformat()
            if verbose > 0:
                print(f"\033[32m\t+ Response received from {args.server_host}:{args.server_port} -> {client_ip}:{client_port}.\033[0m")
            if verbose > 0:
                try:
                    rtt = calculate_difference_timestamp(message["timestamp_send"], timestamp_response)
                    print(f"Round-trip time of the message: {rtt} ms")
                except Exception as e:
                    print(f"Could not calculate round-trip time: {e}")
            response_data = response.decode()
            if verbose > 2: print(f"+ Server response: {response_data}")
            message = json.loads(response_data)
            message["timestamp_recv"] = timestamp_response
            message["server_response"] = True
            message["client_ip"] = client_ip

        except socket.timeout:
            if verbose > 0:
                print(f"\033[31m\t- No response from {args.server_host}:{args.server_port}/{args.protocol.upper()}.\033[0m")

    dados["tests"].append(message)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4)

    if verbose > 0:
        print(f"Writing to file: {json.dumps(message, indent=4)}")

except (socket.gaierror, socket.herror, socket.timeout, ConnectionResetError, OSError) as e:
    if verbose > 0: print(f"Communication error: {e}")
    message["status"] = '0'
    message["status_msg"] = "Firewall Drop or Network Error"
    dados["tests"].append(message)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4)
    if verbose > 0:
        print(f"Writing to file: {json.dumps(message, indent=4)}")

finally:
    if client_sock:
        client_sock.close()

print(json.dumps(message, indent=4))
sys.exit(0)
