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

        # Frame em baixo as abas
        frame_botton = ttk.Frame(self.root)
        frame_botton.pack(side=tk.BOTTOM, pady=6)
        
        self.button_uptate_host = ttk.Button(frame_botton, text="Atualizar Hosts", command=self.update_hosts)
        self.button_uptate_host.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        #self.button_uptate_host.pack(padx=5, pady=5)

        self.button_save_tests = ttk.Button(frame_botton, text="Salvar", command=self.save_tests)
        self.button_save_tests.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        #self.button_save_tests.pack(padx=5, pady=5)

        self.button_save_tests_as = ttk.Button(frame_botton, text="Salvar como", command=self.save_tests_as)
        self.button_save_tests_as.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        #self.button_save_tests_as.pack(padx=5, pady=5)

        frame_botton.grid_columnconfigure(0, weight=1)
        frame_botton.grid_columnconfigure(1, weight=1)
        frame_botton.grid_columnconfigure(2, weight=1)


        # Lista para armazenar os testes
        self.tests = []

        # Lista de labels
        self.test_labels = []

        # Obtém dados de container e hosts
        #self.
        self.containers_data = containers.extract_containerid_hostname_ips( )  # obtém as informações do hosts (hostname, interfaces, ips))

        # A função extract_containerid_hostname_ips já retorna uma lista de dicionários
        #self.containers_data = self.hosts
        #print(f"self.containers_data: {self.containers_data}")

        # Criando a interface das abas
        self.create_hosts_tab()
        self.create_firewall_tab()
        # Reinicia os servidores
        self.start_servers()

    def create_hosts_tab(self):
        """Cria a interface da aba de Hosts"""

        self.top_frame = tk.Frame(self.hosts_frame)
        self.top_frame.pack(pady=10)

        ttk.Label(self.top_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(padx=10)

        # Botão para Ligar todos os servidores nos containers
        ttk.Button(self.top_frame, text="Ligar Servidores", command=self.start_servers).pack(side=tk.LEFT, padx=10)

        # Frame para os botões inferiores
        self.bottom_frame = tk.Frame(self.hosts_frame)
        self.bottom_frame.pack(pady=10)

        self.apresenta_tela_hosts()

    def edit_ports(self, container_id, hostname):
        """Abre uma nova janela para editar as portas do host"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Ports for Container {container_id} - {hostname}:")
        popup.geometry("400x300")  # Aumentei o tamanho para acomodar os botões

        portas = containers.get_port_from_container(container_id)
    
        ttk.Label(popup, text=f"Opened Ports from {hostname}", font=("Arial", 10)).pack(pady=5)

        # Cria a Treeview para exibir as portas
        colunas = ("Protocolo", "Porta")
        tabela_portas = ttk.Treeview(popup, columns=colunas, show="headings", selectmode="browse")
        tabela_portas.heading("Protocolo", text="Protocolo")
        tabela_portas.heading("Porta", text="Porta")
        tabela_portas.column("Protocolo", width=150, anchor=tk.CENTER)
        tabela_portas.column("Porta", width=100, anchor=tk.CENTER)
        tabela_portas.pack(pady=10)

        # Preenche a Treeview com as portas existentes
        for protocolo, porta in portas:
            tabela_portas.insert("", tk.END, values=(protocolo, porta))

        # Cria um frame para os botões
        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(pady=10)

        # Botão para adicionar linha
        botao_adicionar = ttk.Button(frame_botoes, text="Adicionar Porta", command=lambda: self.adicionar_linha(tabela_portas))
        botao_adicionar.pack(side=tk.LEFT, padx=5)

        # Botão para remover linha
        botao_remover = ttk.Button(frame_botoes, text="Remover Porta", command=lambda: self.remover_linha(tabela_portas))
        botao_remover.pack(side=tk.LEFT, padx=5)

        ttk.Button(popup, text="Recarregar Portas", command=lambda: self.salvar_portas_em_arquivo(container_id, tabela_portas)).pack(pady=10)

        # Função para adicionar uma nova linha
    def adicionar_linha(self, tabela_portas):
        """Abre uma nova janela para adicionar uma porta à Treeview"""
        popup = tk.Toplevel()
        popup.title("Adicionar Porta")
        popup.geometry("300x150")

        # Função para validar e adicionar a porta
        def adicionar_porta():
            protocolo = combo_protocolo.get().strip().upper()
            porta = entry_porta.get().strip()

            # Valida o protocolo
            if protocolo not in ["TCP", "UDP"]:
                messagebox.showerror("Erro", "Protocolo inválido! Escolha TCP ou UDP.")
                return

            # Valida a porta
            try:
                porta = int(porta)
                if porta < 0 or porta > 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Porta inválida! Deve ser um número entre 0 e 65535.")
                return

            # Verifica se a combinação protocolo/porta já existe na tabela
            for linha in tabela_portas.get_children():
                valores = tabela_portas.item(linha, "values")
                if valores[0].upper() == protocolo and valores[1] == str(porta):
                    messagebox.showerror("Erro", f"A porta {porta}/{protocolo} já existe na tabela!")
                    return

            # Adiciona a nova porta à Treeview
            tabela_portas.insert("", tk.END, values=(protocolo, porta))
            popup.destroy()  # Fecha a janela popup

        # Campo para selecionar o protocolo
        ttk.Label(popup, text="Protocolo:").pack(pady=5)
        combo_protocolo = ttk.Combobox(popup, values=["TCP", "UDP"], state="readonly")
        combo_protocolo.set("TCP")  # Valor padrão
        combo_protocolo.pack(pady=5)

        # Campo para inserir a porta
        ttk.Label(popup, text="Porta:").pack(pady=5)
        entry_porta = ttk.Entry(popup)
        entry_porta.pack(pady=5)

        # Botão para adicionar a porta
        ttk.Button(popup, text="Adicionar", command=adicionar_porta).pack(pady=10)

    # Função para remover a linha selecionada
    def remover_linha(self, tabela_portas):
        print("remover")
        selecionado = tabela_portas.selection()
        if selecionado:  # Verifica se há algo selecionado
            tabela_portas.delete(selecionado)

    def salvar_portas_em_arquivo(self, containerId, tabela_portas, nome_arquivo="tmp_conf/portas.conf"):
        """
        Salva as portas e protocolos da Treeview em um arquivo, no formato "porta/protocolo".
        
        :param tabela_portas: A Treeview contendo as colunas "Protocolo" e "Porta".
        :param nome_arquivo: Nome do arquivo onde os dados serão salvos.
        """
        try:
            with open(nome_arquivo, "w") as arquivo:
                # Percorre todas as linhas da Treeview
                for linha in tabela_portas.get_children():
                    # Obtém os valores da linha (protocolo e porta)
                    valores = tabela_portas.item(linha, "values")
                    if len(valores) == 2:  # Verifica se há dois valores (protocolo e porta)
                        protocolo, porta = valores
                        # Escreve no arquivo no formato "porta/protocolo"
                        arquivo.write(f"{porta}/{protocolo}\n")
            print(f"Portas salvas com sucesso no arquivo {nome_arquivo}!")
        except Exception as e:
            print(f"Erro ao salvar as portas: {e}")
        
        # recarrega essas portas no container ligando o sevidor com as novas portas.
        self.reload_ports(containerId, nome_arquivo)
        # reinicia os servidor
        containers.start_server(containerId)

        

    def reload_ports(self, container_id, nome_arquivo):
        """Salvar as portas abertas (lógica futura)"""
        print(f"Recarregar portas do {container_id}")

        containers.copy_ports2server(container_id, nome_arquivo)

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
        # Ordena a lista por ordem crescente
        #self.hosts_display.sort() # TODO - ver se ao ordenar, se acontece algo de estranho nos teste, tal como, dá erro de rede ao enviar TCP/80 do host1 para o host2, mas o contrário não (em um cenário com três hosts), mas no comando direto no host1 funciona normal!

        protocols = ["TCP", "UDP", "ICMP"]

        #configurando stilo - para o readonly não ficar cinza
        style = ttk.Style()
        style.map("TCombobox", fieldbackground=[("readonly", "white")])

        # Componentes de entrada
        ttk.Label(frame_entrada, text="Source IP:").grid(row=0, column=0)
        self.src_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.src_ip.current(0)
        self.src_ip.grid(row=1, column=0)
        #permite edição no combobox
        #self.src_ip["state"] = "normal"
        # Vincula o evento de seleção
        #self.src_ip.bind("<<ComboboxSelected>>", self.combobox_add_value)


        ttk.Label(frame_entrada, text="Destination IP:").grid(row=0, column=1)
        self.dst_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25)
        if len(self.containers_data) > 1: # verifica se há mais que um elemento na lista de hosts, se não houver não dá para setar o segundo como padrão.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

        self.dst_ip.grid(row=1, column=1)
        # Vincula o evento de seleção
        self.dst_ip["state"] = "normal"

        # Vincula o evento de seleção
        #self.dst_ip.bind("<Return>", self.combobox_add_value)

        ttk.Label(frame_entrada, text="Protocol:").grid(row=0, column=2)
        self.protocol = ttk.Combobox(frame_entrada, values=protocols, width=6, state="readonly", style="TCombobox")
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

        # Frame legenda
        self.frame_legenda_testes = ttk.LabelFrame(self.firewall_frame, text="Legenda")
        self.frame_legenda_testes.pack(side="bottom", fill="x", padx=20, pady=15)
        self.frame_legenda_testes.pack_propagate(False)
        self.frame_legenda_testes.config(width=700, height=50)

        tk.Label(self.frame_legenda_testes, bg="green", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Teste realizado com sucesso.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="red", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Teste realizado NÃO obteve sucesso.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="yellow", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Falha durante o teste (ex. erro em: IP, GW, DNS, Servidor.)", font=("Arial", 10)).pack(side="left")

        # Variável para armazenar o índice do teste sendo editado
        self.indice_edicao = None

    def validar_ip_ou_dominio(self, string):
        # Regex para IP (IPv4)
        regex_ip = r'^\d+\.\d+\.\d+\.\d+$'
        
        # Regex para domínio (ex: google.com, www.exemplo.com.br)
        regex_dominio = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(regex_ip, string):
            return True
        elif re.match(regex_dominio, string):
            return True
        else:
            return False
    
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
        
        if self.dst_ip.get() not in self.hosts_display:
            if self.validar_ip_ou_dominio(self.dst_ip.get()) == False:
                messagebox.showwarning(f"Endereço inválido", "O endereço deve ou: \n1. estar na lista, \n2. ser um IP (8.8.8.8), \n3. um domínio (www.google.com.br).")
                return
            else: # se for fora da lista de hosts do cenário, por enquanto só é possível realizar testes de ping.
                if self.protocol.get() != "ICMP":
                    messagebox.showwarning(f"Protocolo inválido", "Infelizmente nesta versão só é possível testar hosts externos utilizando ICMP (ping).")
                    return
        # TODO - se for alterado o destino, nestar versão do sistema só pode utilizar o protocolo icmp, não dá para utilizar tcp ou udp, pq o servidor (se existir) não vai reconhecer a mensagem enviada.
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
            #test_str = f"Container ID: {container_id} | {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})"
            test_str = f"{src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})"

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
    
    def extrair_ip_semParenteses(self, string):
        match = re.search(r'\(?(\d+\.\d+\.\d+\.\d+)\)?', string)  
        return match.group(1) if match else None
    
    def extrair_dominio(self, string):
        match = re.search(r'\(?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\)?', string)
        return match.group(1) if match else None
    
    def extrair_destino(self, dst_ip):
        temp_dst_ip =  self.extrair_ip(dst_ip)
        print(f"temp_dst_ip {temp_dst_ip}")

        if temp_dst_ip != None:
            dst_ip = temp_dst_ip
        else:
            print("sem parenteses")
            temp_dst_ip = self.extrair_ip_semParenteses(dst_ip)
            if temp_dst_ip != None:
                dst_ip = temp_dst_ip
            else:
                print("dominio")
                temp_dst_ip = self.extrair_dominio(dst_ip)
                if temp_dst_ip != None:
                    dst_ip = temp_dst_ip
                else:
                    print("invalido")
                    print(f"\033[33mNão foi possível estrair o IP de destino na interface:\n\tO endereço de destino deve ser um IP ou domínio, tal como: 8.8.8.8 ou www.google.com.\033[0m")
                    return None
        return dst_ip    

    def testar_linha(self, indice):
        """Executa o teste individual"""
        teste = self.tests[indice]
        teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected = teste

        # trocar cor da label
        test_label = self.test_labels[indice]
        
        # TODO - aceitar nomes ou IPs, também seria legal permitir que o usuário teste sítes, ou outros serviços, mas tem que pensar bem em como isso pode ser feito (ai não seria no esquedo do software cliente servidor - teria que ser cliente http, cliente ssh, etc... talvez com nmap, nc, etc)!
        #print(f"valor de dst_ip antes de extrair_ip: {dst_ip}")
        
        # se não consegiu extrair o IP de destino digitado pelo usuário para
        dst_ip = self.extrair_destino(dst_ip)
        if dst_ip == None: return

        print(f"Teste executado - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

        result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

        try:
            result = json.loads(result_str)
            print(f"O retorno do comando no host é {result_str}")
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON recebido do host:", e)

        # print()
        # for lbl in self.test_labels:
        #     print(f"testar linha: {lbl}")

        # TODO - para preencher a linha com a cor tem quem comparar qual era a expectativa do teste
        self.colorir_labels_resultado(expected, test_label, result)

    def colorir_labels_resultado(self, expected, test_label, result):
        if (result["status"] != '0'):
            # ocorreu um erro , tal como a rede do host não estava configurada.
            print(f"\033[33mHouve algum erro com o host ao enviar o pacote, tal como: configuração errada da rede - IP, GW, etc.\033[0m")
            test_label.config(background="yellow", foreground="black")
        elif (result["server_response"] == True and expected == "yes") or (result["server_response"] == False and expected == "no"):
            print(f"\033[32mTeste ocorreu conforme esperado.\033[0m")
            # trocar cor da label
            test_label.config(background="lightgreen", foreground="black")
        else:
            if result["status"] == '0': # esperavase sucesse e isso não foi obtido
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
            
            # se não consegiu extrair o IP de destino digitado pelo usuário para
            dst_ip = self.extrair_destino(dst_ip)
            if dst_ip == None: return

            print(f"Teste executado - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
            except json.JSONDecodeError as e:
                print("Erro ao decodificar JSON:", e)

            self.colorir_labels_resultado(expected, test_label, result)

            indice+=1


    def start_servers(self):
        """Inicia server.py nos containers"""
        print("start_servers")
        # TODO - controlar se houve erro ao iniciar o servidor e em qual container.
        for container in self.containers_data:
            container_id = container["id"]
            containers.start_server(container_id)


    def update_hosts(self):
        """Atualiza dados dos hosts/containers - verifica por exemplo se algum container foi criado ou exluido, se alguma configuração de rede mudou, etc"""
        print("update_hosts")

        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        self.containers_data = containers.extract_containerid_hostname_ips( )  # obtém as informações do hosts (hostname, interfaces, ips))

        self.apresenta_tela_hosts( )

        # Lista de valores exibidos no Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # se não houver elementos apresenta uma mensagem
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]
        # ordena nomes no combobox
        #self.hosts_display.sort()
        self.src_ip["values"] = self.hosts_display
        self.dst_ip["values"] = self.hosts_display
        self.src_ip.current(0)
        if len(self.containers_data) > 1: # verifica se há mais que um elemento na lista de hosts, se não houver não dá para setar o segundo como padrão.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

    def apresenta_tela_hosts(self):
        print(f"self.containers_data: {self.containers_data}")
        cont = containers.getContainersHostNames()
        print(f"cont :  {json.dumps(cont, indent=4)}")

        row_index = 0  # Linha inicial na grid

        # Carrega os ícones
        power_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  # Substitua pelo caminho correto do ícone
        status_on_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  # Ícone para servidor ligado
        status_off_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  # Ícone para servidor desligado

        for host in cont:
            print(f"ID: {host['id']}")
            print(f"Nome: {host['nome']}")
            print(f"Hostname: {host['hostname']}")
            print("Interfaces:")

            status = "Ligado" # TODO - criar função para ver se o status do servidor do host está ligado ou desligado.

            container_id = host["id"]
            container_name = host["nome"]
            hostname = host["hostname"]

            # Criando um frame para cada host
            frame = ttk.Frame(self.bottom_frame)
            frame.grid(row=row_index, column=0, columnspan=3, sticky="w", padx=10, pady=5)

            # Botão para editar portas do host
            btn = ttk.Button(frame, text=f"{hostname}", command=lambda cid=container_id: self.edit_ports(cid, hostname))
            btn.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Label com informações do container
            lbl_container = ttk.Label(frame, text=f"Container: {container_id} - {container_name}", font=("Arial", 10))
            lbl_container.grid(row=0, column=1, padx=5, pady=2, sticky="w")

            row_index += 1  # Move para a próxima linha

            for interface in host['interfaces']:
                print(f"  - Interface: {interface['nome']}")
                if_name = interface['nome']

                # Criando um sub-frame para alinhar interfaces e IPs juntos
                interface_frame = ttk.Frame(frame)
                interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)

                # TODO - percebi que o comando ip mosta os IPs da interface mesmo que esta interface esteja desligada DOWN.
                # Label com o nome da interface
                lbl_interface = ttk.Label(interface_frame, text=f"Interface: {if_name}", font=("Arial", 10, "bold"))
                lbl_interface.grid(row=0, column=0, sticky="w")

                ip_index = 1
                for ip in interface['ips']:
                    lbl_ip = ttk.Label(interface_frame, text=f"IP: {ip}", font=("Arial", 10))
                    lbl_ip.grid(row=ip_index, column=0, padx=20, sticky="w")
                    ip_index += 1

                # Status do servidor
                lbl_status = ttk.Label(interface_frame, text=f"Status do servidor: {status}", font=("Arial", 10))
                lbl_status.grid(row=ip_index, column=0, padx=5, sticky="w")
                

                # Botão de Liga/Desliga com ícone
                btn_toggle = ttk.Button(interface_frame, image=power_icon, command=lambda cid=container_id: self.toggle_server(cid))
                btn_toggle.image = power_icon  # Mantém a referência para evitar garbage collection
                btn_toggle.grid(row=ip_index, column=1, padx=10, pady=5, sticky="w")

                row_index += 2  # Move para a próxima linha no layout

            row_index += 1  # Linha extra para separar os hosts

    # TODO - fazer o botão atualizar o status do servidor do container de ligado para desligado1 (passar a variável do botão)
    def toggle_server(self, container_id):
        print(f"Toggling server {container_id}")
        containers.get_port_from_container(container_id)

    def save_tests(self):
        print("Salvar testes")

    def save_tests_as(self):
        print("Salvar testes como...")
    
    def combobox_add_value(self, event):
        print("Adiciona valor novo combobox")
        novo_valor = self.dst_ip.get().strip()  # Obtém e limpa espaços extras do valor digitado
        if novo_valor and novo_valor not in self.hosts_display:
            self.hosts_display.append(novo_valor)
            self.dst_ip["values"] = self.hosts_display
            self.dst_ip.set(novo_valor)


# Executando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
