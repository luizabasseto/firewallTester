import subprocess
import os
import json
import shlex

from . import docker_host 
from . import containers 

class ContainerManager:
    def __init__(self, docker_image_name="firewall_tester"):
        self.docker_image_name = docker_image_name


    def _run_command(self, command_list):
        try:
            return subprocess.run(command_list, capture_output=True, text=True, encoding='utf-8')
        except FileNotFoundError:
            return subprocess.CompletedProcess(
                command_list, 1, 
                stderr="Comando 'docker' não encontrado. Verifique se o Docker está instalado e no PATH do sistema.",
                stdout=""
            )
        except Exception as e:
            return subprocess.CompletedProcess(command_list, 1, stderr=str(e), stdout="")

    def get_all_containers_data(self):
        cmd = [
            "docker", "ps",
            "--filter", f"ancestor={self.docker_image_name}",
            "--format", "{{json .}}"
        ]
        result = self._run_command(cmd)
        if result.returncode != 0:
            print(f"Erro ao buscar containers: {result.stderr}")
            return []

        hosts = []
        for line in result.stdout.strip().splitlines():
            try:
                data = json.loads(line)
                host_details = {
                    "id": data.get("ID", "")[:12],
                    "hostname": data.get("Names", ""),
                    "nome": data.get("Names", ""), 
                    "interfaces": [] 
                }
                hosts.append(host_details)
            except json.JSONDecodeError:
                continue
        return hosts

    def get_hosts_for_combobox(self):

        all_hosts = self.get_all_containers_data()
        return [(host['hostname'], host['id']) for host in all_hosts]

    def check_server_status(self, host_id):
        cmd = ["docker", "exec", host_id, "pgrep", "-f", "server.py"]
        result = self._run_command(cmd)
        status = "on" if result.returncode == 0 and result.stdout.strip() else "off"
        return (True, status)

    def start_server(self, host_id):
        cmd = ["docker", "exec", "-d", host_id, "/usr/local/bin/python", "./server.py"]
        result = self._run_command(cmd)
        if result.returncode != 0:
            return (False, result.stderr)
        return (True, "Servidor iniciado.")

    def stop_server(self, host_id):
        cmd = ["docker", "exec", host_id, "pkill", "-f", "server.py"]
        result = self._run_command(cmd)
        if result.returncode > 1:
            return (False, result.stderr)
        return (True, "Servidor parado.")

    def get_firewall_rules(self, host_id, tables_to_check):
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
        cmd = ["docker", "exec", host_id, "cat", container_file_path]
        result = self._run_command(cmd)
        if result.returncode != 0:
            return (False, result.stderr or "Arquivo não encontrado no container.")
        return (True, result.stdout)

    def save_rules_to_local_file(self, rules_string, local_path):
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(rules_string)
            return (True, "Arquivo salvo localmente.")
        except IOError as e:
            return (False, f"Erro ao salvar arquivo local: {e}")

    def apply_firewall_rules(self, host_id, hostname, local_rules_path, 
        local_reset_path, container_dir, reset_first):

        if reset_first:
            container_path = os.path.join(container_dir, os.path.basename(local_reset_path)).replace("\\", "/")
            result = self._copy_and_execute_script(host_id, local_reset_path, container_path)
            if not result[0]:
                return (False, f"Falha no script de reset:\n{result[1]}")

        container_path = os.path.join(container_dir, os.path.basename(local_rules_path)).replace("\\", "/")
        result = self._copy_and_execute_script(host_id, local_rules_path, container_path)
        if not result[0]:
            return (False, f"Falha no script de regras:\n{result[1]}")
            
        return (True, f"Regras aplicadas com sucesso no host {hostname}.")

    def _copy_and_execute_script(self, host_id, local_path, container_path):
        result_copy = self._run_command(["docker", "cp", local_path, f"{host_id}:{container_path}"])
        if result_copy.returncode != 0:
            return (False, result_copy.stderr)
        
        result_exec = self._run_command(["docker", "exec", host_id, "sh", container_path])
        if result_exec.returncode != 0:
            return (False, result_exec.stderr)

        return (True, "Script executado com sucesso.")