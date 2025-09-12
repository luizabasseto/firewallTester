import json
import re

from . import containers

class TestRunner:

    def run_single_test(self, container_id, dst_ip, protocol, dst_port):
        processed_dst_ip = self._extract_destination_host(dst_ip)
        if not processed_dst_ip:
            error_result = {"status": "1", "status_msg": f"Invalid destination: {dst_ip}"}
            return False, error_result

        result_str = containers.run_client_test(container_id, processed_dst_ip, protocol.lower(), dst_port, "1", "2025", "0")
        
        try:
            result_dict = json.loads(result_str)
            return True, result_dict
        except (json.JSONDecodeError, TypeError) as e:
            error_result = {"status": "1", "status_msg": f"JSON Error: {e}"}
            return False, error_result

    def analyze_test_result(self, expected_result, test_output):
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
        ip_match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', destination)
        if ip_match:
            return ip_match.group(1)
        
        regex_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        regex_domain = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(regex_ip, destination) or re.match(regex_domain, destination):
            return destination
        
        return None