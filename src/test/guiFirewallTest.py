#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
import containers
import json

class FirewallGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Firewall Manager")
        self.root.geometry("800x600")

        # Criando o Notebook (abas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Criando as abas
        self.firewall_frame = ttk.Frame(self.notebook)
        self.hosts_frame = ttk.Frame(self.notebook)
        self.config_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.firewall_frame, text="Teste Firewall")
        self.notebook.add(self.hosts_frame, text="Hosts")
        self.notebook.add(self.config_frame, text="Configurações")

        # Dicionário para armazenar hosts (Exemplo: IP -> Hostname)
        self.hosts = {
            "Host1": "192.168.0.1",
            "Host2": "192.168.0.2"
        }

        # TODO - pegar as informações dos hosts como dicionário
        #self.hosts = getContainers.pegaContainers()


        # Criando a interface das abas
        self.create_hosts_tab()
        self.create_firewall_tab()

    def create_hosts_tab(self):
        """Cria a interface da aba de Hosts"""
        ttk.Label(self.hosts_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(pady=10)

        for ip, hostname in self.hosts.items():
            frame = ttk.Frame(self.hosts_frame)
            frame.pack(fill="x", padx=10, pady=5)

            # Botão para editar as portas do host
            btn = ttk.Button(frame, text=f"{hostname}", command=lambda i=ip, h=hostname: self.edit_ports(i, h))
            btn.pack(side="left", padx=5)

            # Label com informações do host
            lbl = ttk.Label(frame, text=f"IP: {ip}", font=("Arial", 10))
            lbl.pack(side="left")

    def edit_ports(self, ip, hostname):
        """Abre uma nova janela para editar as portas do host"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit {hostname} Ports")
        popup.geometry("300x200")

        ttk.Label(popup, text="Opened Ports:", font=("Arial", 10)).pack(pady=5)
        ports_entry = ttk.Entry(popup, width=30)
        ports_entry.pack(pady=5)

        ttk.Button(popup, text="Save", command=lambda: self.save_ports(ip, ports_entry.get())).pack(pady=10)

    def save_ports(self, ip, ports):
        """Salvar as portas abertas (lógica futura)"""
        print(f"Host {ip} agora tem as portas abertas: {ports}")



    def create_firewall_tab(self):
        """Cria a interface para os testes de firewall"""
        ttk.Label(self.firewall_frame, text="Teste de Firewall", font=("Arial", 12)).pack(pady=10)

        frame = ttk.Frame(self.firewall_frame)
        frame.pack(fill="x", padx=10, pady=5)

        #hosts=["Host1", "Host2", "200.200.200.200"]
        cont = containers.getContainersHostNames()

        hosts = containers.extract_hostname_ips(cont)

        protocols=["TCP", "UDP", "ICMP"]

        ipWidth=20
        portWidth=11

        ttk.Label(frame, text="Source IP:").grid(row=0, column=0)
        #src_ip = ttk.Entry(frame)
        src_ip = ttk.Combobox(frame, values=hosts, width=ipWidth)
        src_ip.current(0)
        src_ip.grid(row=1, column=0)

        ttk.Label(frame, text="Destination IP:").grid(row=0, column=1)
        dst_ip = ttk.Combobox(frame, values=hosts, width=ipWidth)
        dst_ip.current(1)
        dst_ip.grid(row=1, column=1)

        ttk.Label(frame, text="Protocol:").grid(row=0, column=2)
        protocol = ttk.Combobox(frame, values=protocols, width=6)
        protocol.current(0)
        protocol.grid(row=1, column=2)

        ttk.Label(frame, text="Src Port:").grid(row=0, column=3)
        src_port = ttk.Entry(frame, width=portWidth, text="*")
        src_port.insert(0, "*")
        src_port.config(state="disabled")
        src_port.grid(row=1, column=3)

        ttk.Label(frame, text="Dst Port:").grid(row=0, column=4)
        dst_port = ttk.Entry(frame, width=portWidth)
        dst_port.insert(0, "80")
        dst_port.grid(row=1, column=4)

        expected = tk.StringVar(value="yes")
        ttk.Label(frame, text="Expected success?").grid(row=0, column=5)
        success_yes = ttk.Radiobutton(frame, text="Yes", variable=expected, value="yes").grid(row=1, column=5)
        success_no =  ttk.Radiobutton(frame, text="No", variable=expected, value="no").grid(row=1, column=6)
        #expected = ttk.Combobox(frame, values=["Yes", "No"], width=12)
        #expected.grid(row=1, column=5)


        # Botão para adicionar novo teste
        ttk.Button(self.firewall_frame, text="Add Test", command=lambda: self.add_test(
            src_ip.get(), dst_ip.get(), protocol.get(), src_port.get(), dst_port.get(), expected.get()
        )).pack(pady=10)


        ttk.Button(self.firewall_frame, text="Run Test", command=self.execute_test).pack(pady=11)

        self.tests_frame = ttk.Frame(self.firewall_frame)
        self.tests_frame.pack(fill="x", padx=10, pady=10)

    def add_test(self, src_ip, dst_ip, protocol, src_port, dst_port, expected):
        """Adiciona um novo teste à interface"""
        if not src_ip or not dst_ip:
            return

        frame = ttk.Frame(self.tests_frame)
        frame.pack(fill="x", pady=2)

        test_str = f"{src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected success: {expected})"
        ttk.Label(frame, text=test_str).pack(side="left")

        ttk.Button(frame, text="Delete", command=lambda: frame.destroy()).pack(side="right")

    def execute_test(self):
        print("Executando teste de firewall...")




# Executando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
