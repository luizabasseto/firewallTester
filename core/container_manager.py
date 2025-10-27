"""Manages interactions with Docker containers for the Firewall Tester."""

import subprocess
import os
import json
from .docker_host import DockerHost
import tempfile

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
            print(f"Erro ao executar comando {' '.join(command_list)}: {e}")
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
        """
        Executa 'ip -4 -json a' dentro de um container.
        Adaptado de get_ip_info_from_docker.
        """
        cmd = ["docker", "exec", container_id, "ip", "-4", "-json", "a"]
        result = self._run_command(cmd, check=True)
        return json.loads(result.stdout)

    def _process_ip_info(self, interfaces_json, host_obj):
        """
        Processa o JSON de IPs e adiciona as interfaces ao objeto DockerHost.
        Adaptado de process_ip_info.
        """
        for interface in interfaces_json:
            if interface.get("ifname") == "lo":
                continue
            
            ifname = interface.get("ifname")
            if ips := [addr.get("local") for addr in interface.get("addr_info", [])]:
                host_obj.add_interface(ifname, ips)
        return host_obj

    def get_all_containers_data(self):
        """
        Função principal que orquestra a busca e processamento dos dados dos hosts.
        Equivalente a getContainersByImageName + extract_containerid_hostname_ips.
        """
        print(f"\nBuscando containers com a imagem contendo: '{self.docker_image_name}'")
        
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
                print(f"Aviso: Não foi possível obter IPs para o host {host.hostname}: {e}")

            host_dict = host.to_dict()
            
            # Garante que haja um IP para exibição, mesmo que seja 'N/A'
            ip_found = "N/A"
            if host_dict["interfaces"]:
                if (first_interface_ips := host_dict["interfaces"][0].get("ips")):
                    ip_found = first_interface_ips[0]
            
            # Adiciona o IP ao dicionário principal para fácil acesso pela UI
            host_dict['ip'] = ip_found
            detailed_hosts.append(host_dict)
        
        return sorted(detailed_hosts, key=lambda x: x["hostname"])
    
    def toggle_server(self, host_id):
        """
        Verifica o status do servidor e o liga ou desliga.
        Retorna (sucesso, novo_status).
        """
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
        return [(host['hostname'], host['id']) for host in all_hosts]

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
        return (True, "Servidor iniciado.")

    def stop_server(self, host_id):
        """Stops the server.py script inside a container."""
        cmd = ["docker", "exec", host_id, "pkill", "-f", "server.py"]
        result = self._run_command(cmd)
        if result.returncode > 1:
            return (False, result.stderr)
        return (True, "Servidor parado.")

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
            return (False, result.stderr or "Arquivo não encontrado no container.")
        return (True, result.stdout)

    def save_rules_to_local_file(self, rules_string, local_path):
        """Saves a string of rules to a local file."""
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(rules_string)
            return (True, "Arquivo salvo localmente.")
        except IOError as e:
            return (False, f"Erro ao salvar arquivo local: {e}")

    def apply_firewall_rules(self, host_id, hostname, rules_string, local_rules_path,
                            local_reset_path, container_dir, reset_first):
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
                error_message = (f"Falha ao executar o comando:\n'{cmd_str}'\n\n"
                                 f"Erro:\n{result.stderr}")
                return (False, error_message)

        return (True, f"Regras aplicadas com sucesso no host {hostname}.")

    def _copy_and_execute_script(self, host_id, local_path, container_path):
        result_copy = self._run_command(["docker", "cp", local_path, f"{host_id}:{container_path}"])
        if result_copy.returncode != 0:
            return (False, result_copy.stderr)

        result_exec = self._run_command(["docker", "exec", host_id, "sh", container_path])
        if result_exec.returncode != 0:
            return (False, result_exec.stderr)

        return (True, "Script executado com sucesso.")
    
    def get_host_ports(self, host_id):
        """
        Lê o arquivo de configuração de portas de dentro de um contêiner.
        Retorna uma lista de tuplas (protocolo, porta).
        """
        # Assume que o arquivo está em /firewallTester/src/conf/ports.conf
        # Você pode tornar este caminho configurável no futuro.
        container_path = "/firewallTester/src/config/ports.conf"
        cmd = ["docker", "exec", host_id, "cat", container_path]
        result = self._run_command(cmd)

        if result.returncode != 0:
            print(f"Aviso: Não foi possível ler o arquivo de portas para {host_id}. Pode não existir. Erro: {result.stderr}")
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

    def update_host_ports(self, host_id, ports_list):
        content = "\n".join([f"{port}/{protocol}" for protocol, port in ports_list])
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".conf", encoding="utf-8") as tmp:
            tmp.write(content)
            local_temp_path = tmp.name

        container_path = "/firewallTester/src/config/ports.conf"
        
        try:
            copy_result = self._run_command(["docker", "cp", local_temp_path, f"{host_id}:{container_path}"])
            if copy_result.returncode != 0:
                return (False, f"Falha ao copiar o arquivo de portas:\n{copy_result.stderr}")

            print(f"Reiniciando servidor em {host_id} para aplicar novas portas...")
            self.stop_server(host_id)
            start_success, msg = self.start_server(host_id)
            if not start_success:
                return (False, f"Falha ao reiniciar o servidor:\n{msg}")
            
            return (True, "Portas atualizadas e servidor reiniciado com sucesso.")
        
        finally:
            if os.path.exists(local_temp_path):
                os.remove(local_temp_path)
