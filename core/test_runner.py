"""
This module defines the TestRunner class, which is responsible for
executing individual firewall tests and analyzing their results.
"""

import json
import re
import subprocess
import sys
from . import containers

class TestRunner:
    """Orchestrates the execution of tests and interpretation of outcomes."""

    def run_single_test(self, container_id, dst_ip, protocol, dst_port):
        """
        Runs a single client test inside a container and returns the result.

        Args:
            container_id (str): The ID of the source container.
            dst_ip (str): The destination IP address or hostname.
            protocol (str): The protocol to use (TCP, UDP, ICMP).
            dst_port (str): The destination port.

        Returns:
            tuple: A tuple containing a boolean for success and a dictionary
                   with the test result.
        """
        print("--- DEBUG: MÉTODO run_single_test CHAMADO ---", file=sys.stderr)
        sys.stderr.flush()
        processed_dst_ip = self._extract_destination_host(dst_ip)
        if not processed_dst_ip:
            error_result = {"status": "1", "status_msg": f"Invalid destination: {dst_ip}"}
            print(f"--- DEBUG: Destino inválido: {dst_ip}", file=sys.stderr)
            sys.stderr.flush()
            return False, error_result

        command = [
            "docker", "exec", container_id,
            "python3",
            "/firewallTester/src/client.py", # <-- Caminho absoluto
            processed_dst_ip,
            protocol.lower(),
            dst_port,
            "1", "2025", "0" # Argumentos padrão
        ]
        
        try:
            print(f"--- DEBUG: Executando comando: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=10)
            
            print("--- DEBUG: Comando finalizado.", file=sys.stderr)
            print(f"--- DEBUG: Return Code: {result.returncode}", file=sys.stderr)
            print(f"--- DEBUG: STDOUT:\n---\n{result.stdout}\n---", file=sys.stderr)
            print(f"--- DEBUG: STDERR:\n---\n{result.stderr}\n---", file=sys.stderr)
            sys.stderr.flush()
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, stderr=result.stderr)
                
            if not result.stdout:
                raise json.JSONDecodeError("A saída do script estava vazia.", "", 0)

            result_dict = json.loads(result.stdout)
            return True, result_dict

        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'stderr') and e.stderr:
                error_msg = e.stderr.strip()
            
            print(f"--- ERRO no TestRunner: {error_msg}", file=sys.stderr)
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
        result_status = "Fail"
        network_flow = "Sent"
        tag = "no"

        if test_output.get("status", "1") != '0':
            result_status = "ERROR"
            network_flow = "Not Sent"
            tag = "error"
        elif test_output.get("server_response"):
            result_status = "Pass"
            network_flow = "Sent/Received"
            if expected_result.lower() == "yes":
                tag = "yes"
        elif not test_output.get("server_response"):
            if expected_result.lower() == "no":
                result_status = "Pass"
                tag = "yesFail"

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