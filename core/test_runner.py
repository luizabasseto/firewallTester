"""
This module defines the TestRunner class, which is responsible for
executing individual firewall tests and analyzing their results.
"""

import json
import re
import subprocess
import sys
from . import containers
import time
import uuid

class TestRunner:
    """Orchestrates the execution of tests and interpretation of outcomes."""
    def _list_open_ports(self, port:str, protocol: str, container_id: str) -> bool:
        """
        Checks if there is a open port on container, checking port and protocol.

        Args:
            port (str): The port to be tested.
            protocol (str): The protocol to use (TCP, UDP).
            container_id (str): The ID of the source container.

        Returns:
            boolean: Returns true if there is a port open on container, otherwise, returns false
        """

        # filter tcp: ss -tln | grep <port>
        # filter upd: ss -uln | grep <port>

        if protocol.lower() == "tcp":
            flag = "-tln"
        else:
            flag = "-uln"

        check_port_command = f"ss {flag} | grep {port}"

        docker_command = [
            "docker", "exec", container_id,
            "sh", "-c", check_port_command
        ]

        try:
            result = subprocess.run(docker_command, capture_output=True, text=True, encoding='utf-8', timeout=10)
            
            if result.returncode != 0 or (not result.stdout):
                return False
            
            return True

        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'stderr') and e.stderr:
                error_msg = e.stderr.strip()
            
            print(f"Error TestRunner: {error_msg}", file=sys.stderr)
            sys.stderr.flush()
            error_result = {"status": "1", "status_msg": f"Execution Error: {error_msg}"}
            return False, error_result

    def _server_log_confirms_packet(self, log_path, test_id, protocol, server_ip=None, server_port=None):
        """Checks whether the server log contains an entry for the packet.

        Args:
            log_path (str): The path to the server log file.
            test_id (str): The unique identifier of the test.
            protocol (str): The protocol to check (TCP, UDP).
            server_ip (str, optional): The server IP address to filter by. Defaults to None.
            server_port (int, optional): The server port to filter by. Defaults to None.

        Returns:
            bool: True if the packet entry is found in the log with matching criteria, False otherwise.
        """
        try:
            with open(log_path, "r", encoding="utf-8") as handle:
                log_data = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        for entry in log_data.get("received", []):
            if str(entry.get("id", "")) != str(test_id):
                continue
            if str(entry.get("protocol", "")).upper() != str(protocol).upper():
                continue
            if server_ip and str(entry.get("server_ip", "")) and str(entry.get("server_ip")) != str(server_ip):
                continue
            if server_port is not None and entry.get("server_port") is not None and int(entry.get("server_port")) != int(server_port):
                continue
            return bool(entry.get("packet_arrived", True))

        return False

    def _server_log_confirms_packet_in_container(
            self,
            container_id,
            timestamp_teste,
            test_id,
            protocol,
            server_ip=None,
            server_port=None,
            client_ip=None,
            client_port=None,
            wait_seconds=1
        ):
        """Reads the server log from a container and checks whether the packet arrived.
        Args:
            container_id (str): The ID of the destination container to query.
            timestamp_teste (str): The timestamp directory containing the server log.
            test_id (str): The unique identifier of the test packet.
            protocol (str): The protocol to check (TCP, UDP, ICMP).
            server_ip (str, optional): The server IP address to filter by. Defaults to None.
            server_port (int, optional): The server port to filter by. Defaults to None.
            client_ip (str, optional): The client IP address to filter by. Defaults to None.
            client_port (str, optional): The client port to filter by. Defaults to None.
            wait_seconds (int, optional): Maximum time to wait for the packet in seconds. Defaults to 1.

        Returns:
            tuple: A tuple of (bool, str) where:
                - bool: True if packet was found and received, False otherwise.
                - str: A descriptive message explaining the result (e.g., "Received by the server",
                        "TCP SYN received on server", or empty string if packet not found).
        """
        log_path = f"log/{timestamp_teste}/server_log.json"
        deadline = time.monotonic() + wait_seconds

        while time.monotonic() < deadline:
            docker_command = ["docker", "exec", container_id, "sh", "-c", f"cat {log_path} 2>/dev/null || true"]
            try:
                result = subprocess.run(docker_command, capture_output=True, text=True, encoding="utf-8", timeout=10)
            except Exception:
                result = None

            if result and result.returncode == 0 and result.stdout.strip():
                try:
                    log_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    log_data = {"received": []}

                for entry in log_data.get("received", []):
                    if str(entry.get("id", "")) != str(test_id):
                        continue
                    if str(entry.get("protocol", "")).upper() != str(protocol).upper():
                        continue
                    if server_ip and str(entry.get("server_ip", "")) and str(entry.get("server_ip")) != str(server_ip):
                        continue
                    if server_port is not None and entry.get("server_port") is not None and int(entry.get("server_port")) != int(server_port):
                        continue
                    return (True, "Received by the server")

            time.sleep(0.2)
        if protocol.lower() == 'tcp':
            path_syn_check = f"log/syn_log.json"
            docker_command_check_syn = ["docker", "exec", container_id, "sh", "-c", f"cat {path_syn_check} 2>/dev/null || true"]
            try:
                result = subprocess.run(docker_command_check_syn, capture_output=True, text=True, encoding="utf-8", timeout=10)
            except Exception:
                result = None

            if result and result.returncode == 0 and result.stdout.strip():
                try:
                    log_syn_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    log_syn_data = {"received": []}
                for entry in log_syn_data.get("received",[]):
                    if server_port is not None and entry.get("server_port") is not None and int(entry.get("server_port")) != int(server_port):
                        continue
                    if client_ip is not None and entry.get("client_ip") is not None and str(entry.get("client_ip") )!= str(client_ip):
                        continue
                    if server_ip and entry.get("server_ip", "") and str(entry.get("server_ip")) != str(server_ip):
                        continue
                    if client_port is not None and str(entry.get("client_port")) is not None and str(entry.get("client_port")) != str(client_port):
                        continue
                    return (True, "TCP SYN recieved on server")
        
        return (False, "") # Packet did not reach destination according to server logs

    def run_single_test(self, container_id_src, dst_ip, protocol, dst_port, container_id_dest):
        """
        Runs a single client test inside a container and returns the result.

        Args:
            container_id_src (str): The ID of the source container.
            dst_ip (str): The destination IP address or hostname.
            protocol (str): The protocol to use (TCP, UDP, ICMP).
            dst_port (str): The destination port.
            container_id_dest: The ID of the destination container

        Returns:
            tuple: A tuple containing a boolean for success and a dictionary
                    with the test result.
        """
        processed_dst_ip = self._extract_destination_host(dst_ip)
        if not processed_dst_ip:
            error_result = {"status": "1", "status_msg": f"Invalid destination: {dst_ip}"}
            print(f"Invalid destiny: {dst_ip}", file=sys.stderr)
            sys.stderr.flush()
            return False, error_result

        if(protocol.lower() != 'icmp'):
            is_port_open = self._list_open_ports(dst_port,protocol, container_id_dest)
            if not is_port_open:
                result_dict_warn = {
                    "status": "portNotOpen",
                    "status_msg": "port is not open on destination container"
                }
                return False, result_dict_warn

        test_id = str(uuid.uuid4())
        command = [
            "docker", "exec", container_id_src,
            "python3",
            # "/firewallTester/src/client.py",
            "core/client.py",
            processed_dst_ip,
            protocol.lower(),
            dst_port,
            test_id, "2025", "0" 
        ]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=10)
            
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, stderr=result.stderr)
                
            if not result.stdout:
                raise json.JSONDecodeError("The script output was empty.", "", 0)

            result_dict = json.loads(result.stdout)

            if(not result_dict.get("server_response")):
                (packet_arrived, message) = self._server_log_confirms_packet_in_container(
                container_id=container_id_dest,
                timestamp_teste=command[9],
                test_id=test_id,
                protocol=protocol,
                server_ip=processed_dst_ip,
                server_port=int(dst_port),
                client_ip=result_dict.get("client_ip", None),
                client_port=result_dict.get("client_port", None)
                )
                result_dict["packet_arrived"] = packet_arrived

                result_dict["status_msg"] = message
                result_dict["message"] = message

            return True, result_dict

        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'stderr') and e.stderr:
                error_msg = e.stderr.strip()
            
            print(f"Error TestRunner: {error_msg}", file=sys.stderr)
            sys.stderr.flush()
            error_result = {"status": "1", "status_msg": f"Execution Error: {error_msg}"}
            return False, error_result


    def analyze_test_result(self, expected_result, test_output):
        """
        Analyzes the output of a test to determine if it passed or failed.

        Args:
            expected_result (str): The expected outcome ('yes' for pass, 'no' for fail).
            test_output (dict): The JSON output from the client test script.

        Returns:
            tuple: A tuple containing a dictionary with analysis details
                   (result, flow, data) and a tag for UI color-coding.
        """
        expected = expected_result.lower()

        if test_output.get("status", "1") != '0':
            result_status = "ERROR"
            network_flow = "Not Sent"
            tag = "error"

        elif test_output.get("server_response"):
            network_flow = "Sent/Received"
            if expected in ["yes", "permitido"]:
                result_status = "Pass"
                tag = "yes"
            else:
                result_status = "Fail"
                tag = "no" 

        elif not test_output.get("server_response"):
            network_flow = "Sent"
            if expected in ["no", "bloqueado"]:
                result_status = "Pass"
                tag = "yesFail"
            else:
                result_status = "Fail"
                tag = "no"

        if "dnat" in test_output:
            network_flow += " (DNAT)"

        return {"result": result_status, "flow": network_flow, "data": str(test_output)}, tag
    
    def _extract_destination_host(self, destination):
        if ip_match := re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', destination):
            return ip_match[1]
        regex_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        regex_domain = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(regex_ip, destination) or re.match(regex_domain, destination):
            return destination

        return None