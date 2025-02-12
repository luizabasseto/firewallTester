#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
import uuid  # Para gerar IDs únicos
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

        # Lista para armazenar os testes
        self.tests = []

        # Obtém dados de container e hosts
        self.cont = containers.getContainersHostNames() # obtém as informações dos containers (id, hostname, etc)
        #self.hosts = containers.extract_hostname_interface_ips(self.cont) # obtém as informações do hosts (hostname, interfaces, ips))
        self.hosts = containers.extract_containerid_hostname_ips(self.cont) # obtém as informações do hosts (hostname, interfaces, ips))

        print(f"self.hosts{self.hosts}")


        # Criando a interface das abas
        self.create_hosts_tab()
        self.create_firewall_tab()

    def create_hosts_tab(self):
        """Cria a interface da aba de Hosts"""
        ttk.Label(self.hosts_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(pady=10)

        # Exemplo de self.containers_data (substitua pelos seus dados reais)
        # self.containers_data = [
        #     {"id": "c1", "hostname": "host1", "ip": "192.168.1.1"},
        #     {"id": "c2", "hostname": "host2", "ip": "192.168.1.2"},
        #     {"id": "c3", "hostname": "host3", "ip": "192.168.1.3"},
        # ]

        for container in self.containers_data:
            container_id = container["id"]
            hostname = container["hostname"]
            ip = container["ip"]

            # Cria um frame para cada host
            frame = ttk.Frame(self.hosts_frame)
            frame.pack(fill="x", padx=10, pady=5)

            # Botão com o hostname (ou container_id, se preferir)
            btn = ttk.Button(frame, text=f"{hostname}", command=lambda cid=container_id: self.edit_ports(cid))
            btn.pack(side="left", padx=5)

            # Exibe o IP do host
            lbl = ttk.Label(frame, text=f"IP: {ip}", font=("Arial", 10))
            lbl.pack(side="left")

            # Se houver mais de um IP ou interfaces, você pode adaptar aqui
            # Exemplo: Se o container tiver múltiplos IPs, exiba todos
            if "interfaces" in container:
                for interface in container["interfaces"]:
                    iface_name = interface["nome"]
                    ips = interface["ips"]
                    for ip in ips:
                        lbl = ttk.Label(frame, text=f"{iface_name}:{ip}; ", font=("Arial", 10))
                        lbl.pack(side="left")

    def edit_ports(self, hostname):
        """Abre uma nova janela para editar as portas do host"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit {hostname} Ports")
        popup.geometry("300x200")

        ttk.Label(popup, text="Opened Ports:", font=("Arial", 10)).pack(pady=5)
        ports_entry = ttk.Entry(popup, width=30)
        ports_entry.pack(pady=5)

        ttk.Button(popup, text="Save", command=lambda: self.save_ports(hostname, ports_entry.get())).pack(pady=10)

    def save_ports(self, hostname, ports):
        """Salvar as portas abertas (lógica futura)"""
        print(f"Host {hostname} agora tem as portas abertas: {ports}")

    def create_firewall_tab(self):
        """Cria a interface para os testes de firewall"""
        ttk.Label(self.firewall_frame, text="Teste de Firewall", font=("Arial", 12)).pack(pady=10)

        # Frame para os campos de entrada
        frame_entrada = ttk.Frame(self.firewall_frame)
        frame_entrada.pack(fill="x", padx=10, pady=5)

        # Exemplo de IPs e protocolos
        hosts_ips = containers.extract_containerid_hostname_ips(self.cont)
        protocols = ["TCP", "UDP", "ICMP"]
        print(f"hosts_ip: {hosts_ips}")

        # Componentes de entrada
        ttk.Label(frame_entrada, text="Source IP:").grid(row=0, column=0)
        self.src_ip = ttk.Combobox(frame_entrada, values=hosts_ips, width=25)
        self.src_ip.current(0)
        self.src_ip.grid(row=1, column=0)

        ttk.Label(frame_entrada, text="Destination IP:").grid(row=0, column=1)
        self.dst_ip = ttk.Combobox(frame_entrada, values=hosts_ips, width=25)
        self.dst_ip.current(1)
        self.dst_ip.grid(row=1, column=1)

        ttk.Label(frame_entrada, text="Protocol:").grid(row=0, column=2)
        self.protocol = ttk.Combobox(frame_entrada, values=protocols, width=6)
        self.protocol.current(0)
        self.protocol.grid(row=1, column=2)

        ttk.Label(frame_entrada, text="Src Port:").grid(row=0, column=3)
        self.src_port = ttk.Entry(frame_entrada, width=11)
        self.src_port.insert(0, "*")
        self.src_port.config(state="disabled")
        self.src_port.grid(row=1, column=3)

        ttk.Label(frame_entrada, text="Dst Port:").grid(row=0, column=4)
        self.dst_port = ttk.Entry(frame_entrada, width=11)
        self.dst_port.insert(0, "80")
        self.dst_port.grid(row=1, column=4)

        ttk.Label(frame_entrada, text="Expected success?").grid(row=0, column=5)
        self.expected = tk.StringVar(value="yes")
        ttk.Radiobutton(frame_entrada, text="Yes", variable=self.expected, value="yes").grid(row=1, column=5)
        ttk.Radiobutton(frame_entrada, text="No", variable=self.expected, value="no").grid(row=1, column=6)

        # Botão para adicionar/editar teste
        self.botao_adicionar = ttk.Button(self.firewall_frame, text="Adicionar", command=self.adicionar_editar_teste)
        self.botao_adicionar.pack(pady=10)

        # Botão para executar todos os testes
        ttk.Button(self.firewall_frame, text="Executar Testes", command=self.executar_todos_testes).pack(pady=10)

        # Frame para exibir os testes adicionados
        self.tests_frame = ttk.Frame(self.firewall_frame)
        self.tests_frame.pack(fill="x", padx=10, pady=10)

        # Variável para armazenar o índice do teste sendo editado
        self.indice_edicao = None

    def adicionar_editar_teste(self):
        """Adiciona ou edita um teste na lista"""
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.indice_edicao is not None:
            # Editar o teste existente, mantendo o ID original
            teste_id = self.tests[self.indice_edicao][0]  # Mantém o ID original
            self.tests[self.indice_edicao] = (teste_id, src_ip, dst_ip, protocol, src_port, dst_port, expected)
            self.indice_edicao = None
            self.botao_adicionar.config(text="Adicionar")
        else:
            # Adicionar novo teste com um ID único
            teste_id = str(uuid.uuid4())  # Gera um ID único
            self.tests.append((teste_id, src_ip, dst_ip, protocol, src_port, dst_port, expected))

        # Limpar os campos de entrada
        self.src_ip.set("")
        self.dst_ip.set("")
        self.protocol.set("")
        self.src_port.delete(0, tk.END)
        self.dst_port.delete(0, tk.END)
        self.expected.set("yes")

        # Atualizar a exibição dos testes
        self.atualizar_exibicao_testes()

    def atualizar_exibicao_testes(self):
        """Atualiza a exibição dos testes na interface"""
        for widget in self.tests_frame.winfo_children():
            widget.destroy()

        for i, teste in enumerate(self.tests):
            teste_id, src_ip, dst_ip, protocol, src_port, dst_port, expected = teste

            frame = ttk.Frame(self.tests_frame)
            frame.pack(fill="x", pady=2)

            # Exibir os dados do teste
            test_str = f"{src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})"
            ttk.Label(frame, text=test_str).pack(side="left")

            # Botões de testar, editar e excluir
            ttk.Button(frame, text="Testar", command=lambda idx=i: self.testar_linha(idx)).pack(side="left", padx=5)
            ttk.Button(frame, text="Editar", command=lambda idx=i: self.editar_teste(idx)).pack(side="left", padx=5)
            ttk.Button(frame, text="Excluir", command=lambda idx=i: self.excluir_teste(idx)).pack(side="left", padx=5)

    def editar_teste(self, indice):
        """Preenche os campos de entrada com os dados do teste selecionado para edição"""
        _, src_ip, dst_ip, protocol, src_port, dst_port, expected = self.tests[indice]

        self.src_ip.set(src_ip)
        self.dst_ip.set(dst_ip)
        self.protocol.set(protocol)
        self.src_port.delete(0, tk.END)
        self.src_port.insert(0, src_port)
        self.dst_port.delete(0, tk.END)
        self.dst_port.insert(0, dst_port)
        self.expected.set(expected)

        # Armazenar o índice do teste sendo editado
        self.indice_edicao = indice
        self.botao_adicionar.config(text="Salvar Edição")

    def excluir_teste(self, indice):
        """Remove o teste da lista"""
        self.tests.pop(indice)
        self.atualizar_exibicao_testes()

    def testar_linha(self, indice):
        """Executa o teste individual"""
        teste = self.tests[indice]
        print("Teste executado:", teste)

    def executar_todos_testes(self):
        """Executa todos os testes"""
        for teste in self.tests:
            print("Executando todos testes:", teste)

# Executando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
