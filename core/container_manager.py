"""Manages interactions with Docker containers for the Firewall Tester."""

import subprocess
import os
import json

class ContainerManager:
    """
    A class to abstract Docker commands for managing and interacting with
    the test containers.
    """
    def __init__(self, docker_image_name="firewall_tester"):
        self.docker_image_name = docker_image_name

    def _run_command(self, command_list):
        try:
            # `check=False` is used because we handle the return code manually.
            return subprocess.run(
                command_list, capture_output=True, text=True, encoding='utf-8', check=False
            )
        except FileNotFoundError:
            return subprocess.CompletedProcess(
                args=command_list,
                returncode=1,
                stderr=(
                    "Comando 'docker' não encontrado. "
                    "Verifique se o Docker está instalado e no PATH do sistema."
                ),
                stdout=""
            )
        except OSError as e:
            return subprocess.CompletedProcess(args=command_list, returncode=1, stderr=str(e), stdout="")

    def get_all_containers_data(self):
        """
        Retrieves a list of all running containers based on the configured
        Docker image name.
        """
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
        if reset_first:
            container_path = os.path.join(
                container_dir, os.path.basename(local_reset_path)
            ).replace("\\", "/")
            result = self._copy_and_execute_script(host_id, local_reset_path, container_path)
            if not result[0]:
                return (False, f"Falha no script de reset:\n{result[1]}")

        container_path = os.path.join(
            container_dir, os.path.basename(local_rules_path)
        ).replace("\\", "/")
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