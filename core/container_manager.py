"""Manages interactions with Docker containers for the Firewall Tester."""

import subprocess
import json
from .docker_host import DockerHost

class ContainerManager:
    """
    A class to abstract Docker commands for managing and interacting with
    the test containers.
    """
    def __init__(self, docker_image_name="firewall_tester"):
        self.docker_image_name = docker_image_name

    def _run_command(self, command_list, check=False):
        """
        Método auxiliar privado para executar comandos de forma segura.
        Aceita um argumento 'check' para lançar uma exceção em caso de erro.
        """
        try:
            # O 'check' recebido agora é passado para o subprocess.run
            return subprocess.run(command_list, capture_output=True, text=True, encoding='utf-8', check=check)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # Se 'check=True' falhar, a exceção é capturada aqui.
            print(f"Error executing command. {' '.join(command_list)}: {e}")
            # Retorna um objeto de processo com o erro para consistência
            return subprocess.CompletedProcess(command_list, 1, stderr=str(e), stdout="")
    
    def _get_container_info_by_image_filter(self):
        """
        Busca IDs de containers em execução e inspeciona-os para filtrar pela imagem.
        Adaptado de get_container_info_by_filter do código original.
        """
        ps_cmd = ["docker", "ps", "-q"]
        result = self._run_command(ps_cmd, check=True)
        container_ids = result.stdout.strip().splitlines()
        
        matched_containers = []
        for container_id in filter(None, container_ids):
            inspect_cmd = ["docker", "inspect", container_id]
            inspect_result = self._run_command(inspect_cmd)
            if inspect_result.returncode == 0:
                container_data = json.loads(inspect_result.stdout)[0]
                image = container_data["Config"]["Image"]
                
                if self.docker_image_name in image:
                    matched_containers.append({
                        "id": container_id,
                        "hostname": container_data["Config"]["Hostname"],
                        "name": container_data["Name"].strip("/"),
                    })
        return matched_containers

    def _get_ip_info_from_docker(self, container_id):

        cmd = ["docker", "exec", container_id, "ip", "-4", "-json", "a"]
        result = self._run_command(cmd, check=True)
        return json.loads(result.stdout)

    def _process_ip_info(self, interfaces_json, host_obj):
        for interface in interfaces_json:
            if interface.get("ifname") == "lo":
                continue
            
            ifname = interface.get("ifname")
            if ips := [addr.get("local") for addr in interface.get("addr_info", [])]:
                host_obj.add_interface(ifname, ips)
        return host_obj

    def get_all_containers_data(self):
        print(f"\nSearching for containers with the image containing: '{self.docker_image_name}'")
        
        matching_containers_info = self._get_container_info_by_image_filter()
        if not matching_containers_info:
            return []

        detailed_hosts = []
        for container_info in matching_containers_info:
            host = DockerHost(
                container_id=container_info['id'],
                nome=container_info['name'],
                hostname=container_info['hostname']
            )
            
            try:
                interfaces_json = self._get_ip_info_from_docker(container_info['id'])
                host = self._process_ip_info(interfaces_json, host)
            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                print(f"Warning: Could not obtain IP addresses for the host. {host.hostname}: {e}")

            host_dict = host.to_dict()
            
            all_ips = []
            if host_dict["interfaces"]:
                for iface in host_dict["interfaces"]:
                    if ips := iface.get("ips"):
                        all_ips.extend(ips)
            

            if all_ips:
                ip_found = ", ".join(all_ips)
            else:
                ip_found = "N/A"
            
            host_dict['ip'] = ip_found
            detailed_hosts.append(host_dict)
        
        return sorted(detailed_hosts, key=lambda x: x["hostname"])
    
    def toggle_server(self, host_id):
        success_check, current_status = self.check_server_status(host_id)
        if not success_check:
            return (False, "error")

        if current_status == 'on':
            success_action, _ = self.stop_server(host_id)
            return (success_action, "off" if success_action else "on")
        else:
            success_action, _ = self.start_server(host_id)
            return (success_action, "on" if success_action else "off")
    def get_hosts_for_combobox(self):
        """
        Gets a simplified list of hosts (hostname, id) suitable for use in
        a combobox widget.
        """
        all_hosts = self.get_all_containers_data()
        formatted_list = []
        for host in all_hosts:
            hostname = host['hostname']
            container_id = host['id']
            interfaces = host.get('interfaces', [])
            
            found_any_ip = False
            
            for iface in interfaces:
                iface_name = iface.get('nome')
                ips = iface.get('ips', [])
                
                for ip in ips:
                    display_text = f"{hostname} ({ip})"
                    formatted_list.append((display_text, container_id))
                    found_any_ip = True
            
            if not found_any_ip:
                formatted_list.append((hostname, container_id))
            
        return formatted_list

    def check_server_status(self, host_id):
        """Checks if the server.py script is running inside a container."""
        cmd = ["docker", "exec", host_id, "pgrep", "-f", "server.py"]
        result = self._run_command(cmd)
        status = "on" if result.returncode == 0 and result.stdout.strip() else "off"
        return (True, status)

    def start_server(self, host_id):
        """Starts the server.py script inside a container."""
        cmd = ["docker", "exec", "-d", host_id, "/usr/local/bin/python", "./server.py"]
        result = self._run_command(cmd)
        if result.returncode != 0:
            return (False, result.stderr)
        return (True, "Server started.")

    def stop_server(self, host_id):
        """Stops the server.py script inside a container."""
        cmd = ["docker", "exec", host_id, "pkill", "-f", "server.py"]
        result = self._run_command(cmd)
        if result.returncode > 1:
            return (False, result.stderr)
        return (True, "Server stopped.")

    def get_firewall_rules(self, host_id, tables_to_check):
        """
        Retrieves the current iptables rules from a container for specified tables.
        """
        rules = {}
        for table, should_check in tables_to_check.items():
            if not should_check:
                continue
            cmd = ["docker", "exec", host_id, "iptables", "-t", table, "-L", "-n", "-v"]
            result = self._run_command(cmd)
            if result.returncode != 0:
                return (False, result.stderr)
            rules[table] = result.stdout
        return (True, rules)

    def get_rules_from_file(self, host_id, container_file_path):
        """Reads the content of a file from within a container."""
        cmd = ["docker", "exec", host_id, "cat", container_file_path]
        result = self._run_command(cmd)
        if result.returncode != 0:
            return (False, result.stderr or "File not found in container.")
        return (True, result.stdout)

    def save_rules_to_local_file(self, rules_string, local_path):
        """Saves a string of rules to a local file."""
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(rules_string)
            return (True, "File saved locally.")
        except IOError as e:
            return (False, f"Error saving local file: {e}")

    def apply_firewall_rules(self, host_id, hostname, rules_string,reset_first):
        """
        Applies firewall rules to a container.

        (R0913): This method has many arguments, which is a design choice to keep
        the core logic together. They could be grouped into a data class in a
        future refactor.
        """
        commands_to_run = []
        
        # Comandos de reset (agora sem o -P FORWARD ACCEPT)
        if reset_first:
            commands_to_run.extend([
                "iptables -F FORWARD",
                "iptables -F INPUT",
                "iptables -F OUTPUT",
                "iptables -X",
                "iptables -t nat -F",
                "iptables -t nat -X",
                "iptables -t mangle -F",
                "iptables -t mangle -X"
            ])

        for line in rules_string.strip().splitlines():
            clean_line = line.strip()
            if clean_line and not clean_line.startswith('#'):
                commands_to_run.append(clean_line)

        for cmd_str in commands_to_run:
            cmd_list = ["docker", "exec", host_id, "sh", "-c", cmd_str]
            
            result = self._run_command(cmd_list)
            
            if result.returncode != 0:
                error_message = (f"Failed to execute the command:\n'{cmd_str}'\n\n"
                                 f"Error:\n{result.stderr}")
                return (False, error_message)

        return (True, f"Rules successfully applied to the host. {hostname}.")

    def _copy_and_execute_script(self, host_id, local_path, container_path):
        result_copy = self._run_command(["docker", "cp", local_path, f"{host_id}:{container_path}"])
        if result_copy.returncode != 0:
            return (False, result_copy.stderr)

        result_exec = self._run_command(["docker", "exec", host_id, "sh", container_path])
        if result_exec.returncode != 0:
            return (False, result_exec.stderr)

        return (True, "Script executed successfully.")
    
    def get_host_ports(self, host_id):
        container_path = "/firewallTester/src/conf/ports.conf"
        cmd = ["docker", "exec", host_id, "cat", container_path]
        result = self._run_command(cmd)
        if result.returncode != 0:
            return [] 

        ports = []
        for line in result.stdout.strip().splitlines():
            if '/' in line:
                try:
                    port, protocol = line.strip().split('/')
                    ports.append((protocol.upper(), port))
                except ValueError:
                    continue
        return ports

    def update_host_ports(self, host_id, ports_list, local_ports_file_path):
        content = "\n".join([f"{port}/{protocol.upper()}" for protocol, port in ports_list])
        
        try:
            with open(local_ports_file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            return (False, f"Failed to save local file: {e}")

        container_path = "/firewallTester/src/conf/ports.conf"
        copy_result = self._run_command(["docker", "cp", local_ports_file_path, f"{host_id}:{container_path}"])
        if copy_result.returncode != 0:
            return (False, f"Failed to copy port file:\n{copy_result.stderr}")

        print(f"Restarting server in {host_id} to install new doors...")
        self.stop_server(host_id)
        start_success, msg = self.start_server(host_id)
        if not start_success:
            return (False, f"Server restart failed:\n{msg}")
        
        return (True, "Ports updated and server restarted.")