import subprocess
import os

class ContainerManager:
    def _run_command(self, command_list):
        try:
            return subprocess.run(command_list, capture_output=True, text=True, encoding='utf-8')
        except FileNotFoundError:
            return subprocess.CompletedProcess(command_list, 1, stderr="Comando 'docker' não encontrado. Verifique se o Docker está instalado e no PATH do sistema.", stdout="")

    def _copy_to_container(self, host_id, local_path, container_path):
        command = ["docker", "cp", local_path, f"{host_id}:{container_path}"]
        return self._run_command(command)

    def get_firewall_rules(self, host_id, tables_to_check):
        rules = {}
        try:
            for table, should_check in tables_to_check.items():
                if not should_check:
                    continue
                command = ["docker", "exec", host_id, "iptables", "-t", table, "-L", "-n", "-v"]
                result = self._run_command(command)
                if result.returncode != 0:
                    return (False, result.stderr)
                rules[table] = result.stdout
            return (True, rules)
        except Exception as e:
            return (False, str(e))

    def get_rules_from_file(self, host_id, container_file_path):
        try:
            command = ["docker", "exec", host_id, "cat", container_file_path]
            result = self._run_command(command)
            if result.returncode != 0:
                return (False, result.stderr or "Arquivo não encontrado no container.")
            return (True, result.stdout)
        except Exception as e:
            return (False, str(e))

    def apply_firewall_rules(self, host_id, hostname, rules_string, local_rules_path, 
                             local_reset_path, container_dir, reset_first):

        try:
            with open(local_rules_path, "w", encoding="utf-8") as f:
                f.write(rules_string)
        except IOError as e:
            return (False, f"Erro ao salvar arquivo de regras local: {e}")

        if reset_first:
            container_reset_path = os.path.join(container_dir, os.path.basename(local_reset_path)).replace("\\", "/")
            
            result_copy = self._copy_to_container(host_id, local_reset_path, container_reset_path)
            if result_copy.returncode != 0:
                return (False, f"Falha ao copiar script de reset:\n{result_copy.stderr}")

            result_exec = self._run_command(["docker", "exec", host_id, "sh", container_reset_path])
            if result_exec.returncode != 0:
                return (False, f"Falha ao executar script de reset:\n{result_exec.stderr}")

        container_rules_path = os.path.join(container_dir, os.path.basename(local_rules_path)).replace("\\", "/")
        
        result_copy = self._copy_to_container(host_id, local_rules_path, container_rules_path)
        if result_copy.returncode != 0:
            return (False, f"Falha ao copiar script de regras:\n{result_copy.stderr}")

        # Executa o script de regras
        result_exec = self._run_command(["docker", "exec", host_id, "sh", container_rules_path])
        if result_exec.returncode != 0:
            return (False, f"Falha ao executar script de regras:\n{result_exec.stderr}")

        return (True, f"Regras aplicadas com sucesso no host {hostname}.")