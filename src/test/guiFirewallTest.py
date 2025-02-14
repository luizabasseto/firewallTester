#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import uuid  # Para gerar IDs únicos
import containers
import json
import re

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

        # Lista de labels
        self.test_labels = []

        # Obtém dados de container e hosts
        #self.
        self.containers_data = containers.extract_containerid_hostname_ips( )  # obtém as informações do hosts (hostname, interfaces, ips))

        # A função extract_containerid_hostname_ips já retorna uma lista de dicionários
        #self.containers_data = self.hosts
        print(f"self.containers_data: {self.containers_data}")

        # Criando a interface das abas
        self.create_hosts_tab()
        self.create_firewall_tab()

    def create_hosts_tab(self):
        """Cria a interface da aba de Hosts"""

        self.top_frame = tk.Frame(self.hosts_frame)
        self.top_frame.pack(pady=10)

        ttk.Label(self.top_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(padx=10)

        # Botão para Ligar todos os servidores nos containers
        ttk.Button(self.top_frame, text="Ligar Servidores", command=self.start_servers).pack(side=tk.LEFT, padx=10)
        # Botão para executar todos os testes
        ttk.Button(self.top_frame, text="Atualizar Hosts", command=self.update_hosts).pack(padx=10)

        # Frame para os botões inferiores
        self.bottom_frame = tk.Frame(self.hosts_frame)
        self.bottom_frame.pack(pady=10)

        for container in self.containers_data:
            container_id = container["id"]
            hostname = container["hostname"]
            ip = container["ip"]

            # Cria um frame para cada host
            frame = ttk.Frame(self.bottom_frame)
            frame.pack(fill="x", padx=10, pady=5)

            # Botão com o hostname (ou container_id, se preferir)
            btn = ttk.Button(frame, text=f"{hostname}", command=lambda cid=container_id: self.edit_ports(cid))
            btn.pack(side="left", padx=5)

            # Exibe o IP do host
            lbl = ttk.Label(frame, text=f"IP: {ip}", font=("Arial", 10))
            lbl.pack(side="left")

    def edit_ports(self, container_id):
        """Abre uma nova janela para editar as portas do host"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Ports for Container {container_id}")
        popup.geometry("300x200")

        ttk.Label(popup, text="Opened Ports:", font=("Arial", 10)).pack(pady=5)
        ports_entry = ttk.Entry(popup, width=30)
        ports_entry.pack(pady=5)

        ttk.Button(popup, text="Save", command=lambda: self.save_ports(container_id, ports_entry.get())).pack(pady=10)

    def save_ports(self, container_id, ports):
        """Salvar as portas abertas (lógica futura)"""
        print(f"Container {container_id} agora tem as portas abertas: {ports}")

    def create_firewall_tab(self):
        """Cria a interface para os testes de firewall"""
        ttk.Label(self.firewall_frame, text="Teste de Firewall", font=("Arial", 12)).pack(pady=10)

        # Frame para os campos de entrada
        frame_entrada = ttk.Frame(self.firewall_frame)
        frame_entrada.pack(fill="x", padx=10, pady=5)

        # Lista de valores exibidos no Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # se não houver elementos apresenta uma mensagem
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]

        protocols = ["TCP", "UDP", "ICMP"]

        # Componentes de entrada
        ttk.Label(frame_entrada, text="Source IP:").grid(row=0, column=0)
        self.src_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25)
        self.src_ip.current(0)
        self.src_ip.grid(row=1, column=0)

        ttk.Label(frame_entrada, text="Destination IP:").grid(row=0, column=1)
        self.dst_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25)
        if len(self.containers_data) > 1: # verifica se há mais que um elemento na lista de hosts, se não houver não dá para setar o segundo como padrão.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

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
        self.botao_adicionar = ttk.Button(self.firewall_frame, text="Adicionar", command=self.validar_e_adicionar_teste)
        self.botao_adicionar.pack(pady=10)

        # Botão para executar todos os testes
        ttk.Button(self.firewall_frame, text="Executar Testes", command=self.executar_todos_testes).pack(pady=10)

        # Frame para exibir os testes adicionados
        self.tests_frame = ttk.Frame(self.firewall_frame)
        self.tests_frame.pack(fill="x", padx=10, pady=10)

        # Variável para armazenar o índice do teste sendo editado
        self.indice_edicao = None

    def validar_e_adicionar_teste(self):
        """Valida os campos antes de chamar o método adicionar_editar_teste"""
        # Verifica se os campos obrigatórios estão preenchidos

        if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
            messagebox.showwarning("Campos obrigatórios", "Por favor, preencha todos os campos obrigatórios.")
            return
        if not self.dst_port.get().isdigit():
            messagebox.showwarning("Campos obrigatórios", "Por favor, a porta deve ser um número entre 1-65535.")
            return
        try:
            porta = 1<= int(self.dst_port.get())
            if not 1 <= porta <=65536:
                messagebox.showwarning("Campos obrigatórios", "Por favor, a porta deve ser um número entre 1-65535.")
                return
        except ValueError:
            messagebox.showwarning("Porta inválida: erro na conversão.")
            return

        # Se todos os campos estiverem preenchidos, chama o método adicionar_editar_teste
        self.adicionar_editar_teste()

    def adicionar_editar_teste(self):
        """Adiciona ou edita um teste na lista"""
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        # Obtém o ID do container selecionado no Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
        else:
            container_id = "N/A"  # Caso nenhum container seja selecionado

        if self.indice_edicao is not None:
            # Editar o teste existente, mantendo o ID original
            teste_id = self.tests[self.indice_edicao][0]  # Mantém o ID original
            self.tests[self.indice_edicao] = (teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected)
            self.indice_edicao = None
            self.botao_adicionar.config(text="Adicionar")
        else:
            # Adicionar novo teste com um ID único
            teste_id = str(uuid.uuid4())  # Gera um ID único
            self.tests.append((teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected))

        # Limpar os campos de entrada
        # self.src_ip.set("")
        # self.dst_ip.set("")
        # self.protocol.set("")
        # self.src_port.delete(0, tk.END)
        # self.dst_port.delete(0, tk.END)
        # self.expected.set("yes")

        # Atualizar a exibição dos testes
        self.atualizar_exibicao_testes()

    def atualizar_exibicao_testes(self):
        """Atualiza a exibição dos testes na interface"""
        for widget in self.tests_frame.winfo_children():
            widget.destroy()
            self.test_labels = []  # Cria a lista se não existir

        for i, teste in enumerate(self.tests):
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected = teste

            frame = ttk.Frame(self.tests_frame)
            frame.pack(fill="x", pady=2)

            # Exibir os dados do teste
            test_str = f"Container ID: {container_id} | {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})"

            # Salva a label para marcar conforme o teste falhar com ser realizado com sucesso!
            test_label = ttk.Label(frame, text=test_str)
            test_label.pack(side="left")  # Configura o layout

            #if not hasattr(self, 'test_labels'):
            #    self.test_labels = []  # Cria a lista se não existir
            self.test_labels.append(test_label)

            # print()
            # for lbl in self.test_labels:
            #     print(f"atualizar_exibicao_testes: {lbl}")
            #     lbl.config(background="lightgreen", foreground="black")

            # Botões de testar, editar e excluir
            ttk.Button(frame, text="Testar", command=lambda idx=i: self.testar_linha(idx)).pack(side="left", padx=5)
            ttk.Button(frame, text="Editar", command=lambda idx=i: self.editar_teste(idx)).pack(side="left", padx=5)
            ttk.Button(frame, text="Excluir", command=lambda idx=i: self.excluir_teste(idx)).pack(side="left", padx=5)

    def editar_teste(self, indice):
        """Preenche os campos de entrada com os dados do teste selecionado para edição"""
        _, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected = self.tests[indice]

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

    def extrair_ip(self,string):
        match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', string)
        return match.group(1) if match else None

    def testar_linha(self, indice):
        """Executa o teste individual"""
        teste = self.tests[indice]
        teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected = teste

        # trocar cor da label
        test_label = self.test_labels[indice]

        dst_ip =  self.extrair_ip(dst_ip)

        print(f"Teste executado - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

        result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

        try:
            result = json.loads(result_str)
            print(f"O retorno é {result_str}")
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON:", e)

        # print()
        # for lbl in self.test_labels:
        #     print(f"testar linha: {lbl}")

        # TODO - para preencher a linha com a cor tem quem comparar qual era a expectativa do teste
        if (result["server_response"] == True and expected == "yes") or (result["server_response"] == False and expected == "no"):
            print(f"\033[32mTeste ocorreu conforme esperado.\033[0m")
            # trocar cor da label
            test_label.config(background="lightgreen", foreground="black")
        else:
            print(f"\033[31mTeste NÃO ocorreu conforme esperado.\033[0m")
            # trocar cor da label
            test_label.config(background="lightcoral", foreground="black")



    def executar_todos_testes(self):
        """Executa todos os testes"""
        indice=0
        for teste in self.tests:
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected = teste
            print(f"Executando teste - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")
            test_label = self.test_labels[indice]
            dst_ip =  self.extrair_ip(dst_ip)

            print(f"Teste executado - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
            except json.JSONDecodeError as e:
                print("Erro ao decodificar JSON:", e)

            if (result["server_response"] == True and expected == "yes") or (result["server_response"] == False and expected == "no"):
                print(f"\033[32mTeste ocorreu conforme esperado.\033[0m")
                # trocar cor da label
                test_label.config(background="lightgreen", foreground="black")
            else:
                print(f"\033[31mTeste NÃO ocorreu conforme esperado.\033[0m")
                # trocar cor da label
                test_label.config(background="lightcoral", foreground="black")

            indice+=1


    def start_servers(self):
        """Inicia server.py nos containers"""
        print("start_servers")
        for container in self.containers_data:
            container_id = container["id"]
            containers.start_server(container_id)


    def update_hosts(self):
        """Atualiza dados dos hosts/containers - verifica por exemplo se algum container foi criado ou exluido, se alguma configuração de rede mudou, etc"""
        print("update_hosts")

        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        self.containers_data = containers.extract_containerid_hostname_ips( )  # obtém as informações do hosts (hostname, interfaces, ips))

        for container in self.containers_data:
            container_id = container["id"]
            hostname = container["hostname"]
            ip = container["ip"]

            # Cria um frame para cada host
            frame = ttk.Frame(self.bottom_frame)
            frame.pack(fill="x", padx=10, pady=5)

            # Botão com o hostname (ou container_id, se preferir)
            btn = ttk.Button(frame, text=f"{hostname}", command=lambda cid=container_id: self.edit_ports(cid))
            btn.pack(side="left", padx=5)

            # Exibe o IP do host
            lbl = ttk.Label(frame, text=f"IP: {ip}", font=("Arial", 10))
            lbl.pack(side="left")

        # Lista de valores exibidos no Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # se não houver elementos apresenta uma mensagem
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]

        self.src_ip["values"] = self.hosts_display
        self.dst_ip["values"] = self.hosts_display
        self.src_ip.current(0)
        if len(self.dst_ip) > 0:
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

        #for widget in self.firewall_frame.winfo_children():
        #    widget.destroy()
        # TODO - atualizar valores Combobox.
        #self.atualizar_exibicao_testes()
        



# Executando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
