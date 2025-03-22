#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from tkinter import filedialog
import os
import containers
import json
import re
import threading
import webbrowser
import textwrap

# TODO - Padronizar os nomes de variáveis e funções - utilizar nomes em inglês.
# TODO - Deixar todas as mensagens print e gráficas em inglês - botões, labels, etc...
# TODO - Refatorar o código - remover códigos duplicados, ver o que pode ser melhorado talvez com o conceito de orientação à objetos
# TODO - Remover variáveis e códigos que não estão sendo utilizados - pode ter código inútil principalmente pq mudou-se de label para treeview.
# TODO - Aba configuração - ver se é necessária e o que colocar lá.
# TODO - Criar um help para o usuário.
# TODO - Criar um about - informações de crétido, etc...
# TODO - Ver a licença que será utilizada.
# TODO - Pensar se haverá um lugar para editar as regras de firewall, ligar/desligar firewall na interface ou se será tudo no host mesmo.
# TODO - Ao realizar testes verificar se há erros como testar uma porta fechada no servidor, a interface poderia avisar quanto a isso (deixar, mas avisar).
# TODO - Verificar o fluxo da mensagem, tal como, chegou no servidor mas não voltou, indicar isso na interface.
# TODO - Pensar em como mostrar os logs de execução, que vão para o console texto, para a interface, isso ajuda muito a mostrar problemas e o fluxo dos testes.
# TODO - Pensar em como mostrar detalhes do "pacotes" - objetos JSON retornados por cliente/servidor nos testes.
# TODO - No arquivo container.py - ao ligar um servidor em uma porta já em uso por outro programa que não o server.py, verificar se pode realmente matar tal processo.
# TODO - Pensar em como acessar alguns serviços reais, tais como HTTP, SSH, MYSQL, etc. e como mostrar isso na interface, atualmente fora do cliente.py/servidor.py só dá para acessar externo o ICMP.
# TODO - Pensar em testes de pacotes mal formados tal como do nmap ou scapy.
# TODO - sugerir testes que podem ser comuns em ambientes de empresas.
# TODO - sugerir testes baseados nos serviços em execução no ambiente.
# TODO - sugerir testes fundamentados nos testes propostos pelo usuário, tal como: se pediu para host1 acessar HTTP no host3, fazer o contrário também.
# TODO - Esta dando erro quando um servidor não está ligado, mas isso não deveria acontecer -  a mensagem é: Unable to get a response from the hosts! Is GNS3 or the hosts running? dá erra erro no este  - procurar e corrigir! Parece que o problema é que a porta, por exemplo tcp/80, está em uso quando liga o servidor, ai ele desliga o próprio servidor, então a porta 80 não aparece na lista, ai vc adiciona, ai ficam duas portas 80 na lista, ai ele mata ele mesmo, pq o programa está configurado para matar programas que estão ocupando a porta - então tem que: TODO - não aceitar portas duplicadas no arquivo, ele está vendo isso via netstat - # TODO - ver essa história de matar e como matar, pq ele não pode matar ele mesmo!
# TODO - quando está salvando e abrindo os testes salvos, está dando erros de colunar na tree, pq as colunas foram alteradas! rever...

class FirewallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Firewall Tester")
        self.root.geometry("800x600")

        # Criando o Notebook (abas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Criando as abas
        self.firewall_frame = ttk.Frame(self.notebook)
        self.hosts_frame = ttk.Frame(self.notebook)
        self.config_frame = ttk.Frame(self.notebook)
        self.regras_firewall = ttk.Frame(self.notebook)
        self.about_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.firewall_frame, text="Firewall Test")
        self.notebook.add(self.regras_firewall, text="Firewall Rules")
        self.notebook.add(self.hosts_frame, text="Hosts")
        self.notebook.add(self.config_frame, text="Settings")
        self.notebook.add(self.about_frame, text="About")

        # Frame em baixo as abas
        frame_botton = ttk.Frame(self.root)
        frame_botton.pack(side=tk.BOTTOM, pady=6)
        
        # TODO - ao atualizar os dados dos hosts, pode ser necessário mudar dados dos testes, principalmente os IDs dos constainers e talvez IPs dos hosts - tal como tem que ser feito ao carregar os testes de um arquivo - pensar em uma solução única para os dois problemas - talvez precise de intervenção do usuário.
        self.button_uptate_host = ttk.Button(frame_botton, text="Update Hosts", command=self.update_hosts)
        self.button_uptate_host.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.button_quit = ttk.Button(frame_botton, text="Exit", command=self.confirmar_saida)
        self.button_quit.grid(row=0, column=6, padx=10, pady=10, sticky="nsew")
        
        frame_botton.grid_columnconfigure(0, weight=1)
        frame_botton.grid_columnconfigure(1, weight=1)
        frame_botton.grid_columnconfigure(2, weight=1)

        # caminho do nome do arquivo
        self.save_file_path = None

        # Lista para armazenar os testes
        self.tests = []

        # lista de botoes dos hosts
        self.lista_btn_onOff = []

        # Obtém dados de container e hosts
        self.containers_data = containers.extract_containerid_hostname_ips( )  # obtém as informações do hosts (hostname, interfaces, ips))

        # Criando a interface das abas
        self.create_hosts_tab()
        self.create_firewall_tab()
        self.create_regras_firewall_tab()
        # Reinicia os servidores
        self.start_servers()
        self.create_about_tab()

    def create_about_tab(self):
        top_frame = tk.Frame(self.about_frame)
        top_frame.pack(pady=10)

        # Developer Information
        lbl_title = ttk.Label(top_frame, text="About the Software", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # Software Description
        description = "This software was developed with the goal of strengthening network security through practical and efficient firewall testing. More than just a testing tool, it stands out as a valuable educational resource, designed to simplify and enhance the learning process about firewalls. Through an intuitive and interactive interface, students can visualize and experiment with the creation and application of firewall rules, making it easier to understand complex concepts and promoting deeper and more effective learning."

        # Create a frame for the description
        description_frame = ttk.Frame(top_frame)
        description_frame.pack(pady=10, padx=20, fill="x") #fill x para ocupar toda a largura

        # Simulate full justification using textwrap
        wrapped_text = textwrap.fill(description, width=70) #aumentei o width para o texto se espalhar mais

        # Get background color from parent frame
        bg_color = top_frame.cget("background")

        # Use tk.Text for display
        text_widget = tk.Text(description_frame, wrap="word", width=70, height=8, borderwidth=0, highlightthickness=0, background=bg_color) #aumentei o height e o width
        text_widget.insert("1.0", wrapped_text)
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(pady=10, padx=10, fill="x")

        
        # Developer
        lbl_developer_name_head = ttk.Label(top_frame, text="Developer:")
        lbl_developer_name_head.pack()
        lbl_developer_name = ttk.Label(top_frame, text=f"Prof. Luiz Arthur Feitosa dos Santos", font=("Arial", 12, "bold"))
        lbl_developer_name.pack()

        # Clickable Email
        #lbl_email_text = ttk.Label(top_frame, text="Email: ")
        #lbl_email_text.pack()

        lbl_email = ttk.Label(top_frame, text=f"luiz.arthur.feitosa.santos@gmail.com\n", foreground="blue", cursor="hand2")
        lbl_email.pack()
        lbl_email.bind("<Button-1>", lambda e: webbrowser.open_new_tab("mailto:luiz.arthur.feitosa.santos@gmail.com"))

        lbl_institution_head = ttk.Label(top_frame, text="Institution:")
        lbl_institution_head.pack()
        lbl_institution = ttk.Label(top_frame, text=f"UTFPR-CM\n", font=("Arial", 12, "bold"))
        lbl_institution.pack()

        # Clickable Project Link
        lbl_project_link_text = ttk.Label(top_frame, text="Project Link: ")
        lbl_project_link_text.pack()

        lbl_project_link = ttk.Label(top_frame, text=f"https://github.com/luizsantos/firewallTester\n", foreground="blue", cursor="hand2")
        lbl_project_link.pack()
        lbl_project_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester"))

        # Clickable License Link
        lbl_license_text = ttk.Label(top_frame, text="License: ")
        lbl_license_text.pack()

        lbl_license = ttk.Label(top_frame, text=f"GNU GPL v3\n", foreground="blue", cursor="hand2")
        lbl_license.pack()
        lbl_license.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.gnu.org/licenses/gpl-3.0.html"))

        # Help Button
        btn_help = ttk.Button(top_frame, text="Help", command=self.abrir_ajuda)
        btn_help.pack(pady=20)

    
    def abrir_ajuda(self):
        webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester")  # Substitua pelo URL da sua página de ajuda

    def create_hosts_tab(self):
        """Cria a interface da aba de Hosts"""

        self.top_frame = tk.Frame(self.hosts_frame)
        self.top_frame.pack(pady=10)

        ttk.Label(self.top_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(padx=10)

        # Botão para Ligar todos os servidores nos containers
        ttk.Button(self.top_frame, text="Turn on servers", command=self.start_servers).pack(side=tk.LEFT, padx=10)

        # Frame para os botões inferiores
        self.bottom_frame = tk.Frame(self.hosts_frame)
        self.bottom_frame.pack(pady=10)

        self.apresenta_tela_hosts()

    def create_regras_firewall_tab(self):
        """Cria a interface da aba de Hosts"""
        # Frame superior para o título
        frame_titulo = tk.Frame(self.regras_firewall)
        frame_titulo.pack(fill=tk.X)

        ttk.Label(frame_titulo, text="Edit firewall rules on host:", font=("Arial", 12, "bold")).pack(padx=10)
        self.combobox_host_regra_firewall = ttk.Combobox(frame_titulo, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.combobox_host_regra_firewall.pack(pady=10)
        #self.combobox_host_regra_firewall.current(0)
        self.combobox_host_regra_firewall.set("")

        self.combobox_host_regra_firewall.bind("<<ComboboxSelected>>", self.on_combobox_host_regras_firewall_select)

        #label_titulo = tk.Label(frame_titulo, text="Editar regras de firewall", font=("Arial", 12, "bold"))
        #label_titulo.pack(pady=5)

        # Criando LabelFrame para as regras a serem aplicadas
        frame_regras = ttk.LabelFrame(self.regras_firewall, text="Rules to be applied to the firewall")
        frame_regras.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_regras = tk.Text(frame_regras, wrap=tk.NONE, height=10, undo=True)
        self.text_regras.grid(row=0, column=0, sticky="nsew")

        scroll_y_regras = tk.Scrollbar(frame_regras, orient=tk.VERTICAL, command=self.text_regras.yview)
        scroll_y_regras.grid(row=0, column=1, sticky="ns")
        self.text_regras.config(yscrollcommand=scroll_y_regras.set)

        scroll_x_regras = tk.Scrollbar(frame_regras, orient=tk.HORIZONTAL, command=self.text_regras.xview)
        scroll_x_regras.grid(row=1, column=0, sticky="ew")
        self.text_regras.config(xscrollcommand=scroll_x_regras.set)

        self.reset_firewall = tk.IntVar()
        checkbtn_zerar_regras = tk.Checkbutton(frame_regras, text="Automatically reset firewall rules – this should be in your script, but you can do it here.", variable=self.reset_firewall)
        checkbtn_zerar_regras.grid(row=2, column=0, sticky="w")

        frame_regras.grid_columnconfigure(0, weight=1)
        frame_regras.grid_rowconfigure(0, weight=1)

        # Criando LabelFrame para as regras ativas no firewall (inicialmente oculto)
        frame_ativas = ttk.LabelFrame(self.regras_firewall, text="Output ")
        frame_ativas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        #frame_ativas.pack_forget()  # Escondendo inicialmente

        def toggle_frame_ativas():
            if frame_ativas.winfo_ismapped():
                frame_ativas.pack_forget()
                btn_ver_ativas.config(text="Show output")
            else:
                frame_ativas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                btn_ver_ativas.config(text="Hide output")

        def select_all(event):
            event.widget.tag_add("sel", "1.0", "end")
            return "break"

        self.text_ativas = tk.Text(frame_ativas, wrap=tk.NONE, height=10)
        self.text_ativas.grid(row=0, column=0, sticky="nsew")
        self.text_ativas.bind("<Control-a>", select_all)

        self.text_regras.bind("<Control-a>", select_all)

        scroll_y_ativas = tk.Scrollbar(frame_ativas, orient=tk.VERTICAL, command=self.text_ativas.yview)
        scroll_y_ativas.grid(row=0, column=1, sticky="ns")
        self.text_ativas.config(yscrollcommand=scroll_y_ativas.set)
        self.text_ativas.config(state=tk.NORMAL) # não sei pq, mas se não ativas e desativar o text_ativas, o selecionar tudo não funciona no text_regras
        #self.text_ativas.config(state=tk.DISABLED)

        scroll_x_ativas = tk.Scrollbar(frame_ativas, orient=tk.HORIZONTAL, command=self.text_ativas.xview)
        scroll_x_ativas.grid(row=1, column=0, sticky="ew")
        self.text_ativas.config(xscrollcommand=scroll_x_ativas.set)

        frame_ativas.grid_columnconfigure(0, weight=1)
        frame_ativas.grid_rowconfigure(0, weight=1)
        self.btn_listar_regras_firewall = tk.Button(frame_ativas, text="List firewall rules", command=self.listar_regras_firewall)
        self.btn_listar_regras_firewall.grid(row=2, column=0)
        self.btn_listar_regras_firewall.config(state="disabled")

        # Criando os botões
        frame_botoes = tk.Frame(self.regras_firewall)
        frame_botoes.pack(pady=10)

        self.btn_carregar = tk.Button(frame_botoes, text="Retrieve firewall rules", command=self.carregar_regras_firewall)
        self.btn_carregar.pack(side=tk.LEFT, padx=10)
        self.btn_carregar.config(state="disabled")

        self.btn_aplicar = tk.Button(frame_botoes, text="Deploy firewall rules", command=self.aplicar_regras_firewall)
        self.btn_aplicar.pack(side=tk.LEFT, padx=10)
        self.btn_aplicar.config(state="disable")

        #self.btn_zerar = tk.Button(frame_botoes, text="Zerar Regras no firewall", command=self.zerar_regras_firewall)
        #self.btn_zerar.pack(side=tk.LEFT, padx=10)
        #self.btn_zerar.config(state="disable")

        btn_ver_ativas = tk.Button(frame_botoes, text="Hide output", command=toggle_frame_ativas)
        btn_ver_ativas.pack(side=tk.RIGHT, padx=10)

    def on_combobox_host_regras_firewall_select(self, src_ip):
        #print("combobox host regras")
        selected_index = self.combobox_host_regra_firewall.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = [self.containers_data[selected_index]["id"], self.containers_data[selected_index]["hostname"]]
            #print(f"container_data selected_index{selected_index} -  {self.containers_data[selected_index]}")
        else:
            container_id = "N/A"  # Caso nenhum container seja selecionado
        print(container_id)
        self.btn_carregar.config(state="normal")
        self.btn_aplicar.config(state="normal")
        self.btn_listar_regras_firewall.config(state="normal")
        #self.btn_zerar.config(state="normal")
        self.container_id_host_regras_firewall=container_id

    def listar_regras_firewall(self):
        print(f"List firewall rules for host {self.container_id_host_regras_firewall[1]}")
        
        self.text_ativas.delete(1.0, tk.END)

        command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n", "-t", "nat"]
        result = containers.run_command(command)
        self.text_ativas.insert(tk.END, f"\n* Result of the command iptables -t nat -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
        self.text_ativas.insert(tk.END, result.stdout)
        
        command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n"]
        result = containers.run_command(command)
        self.text_ativas.insert(tk.END, f"\n* Result of the command iptables -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
        self.text_ativas.insert(tk.END, result.stdout)

        self.text_ativas.see(tk.END) # rola o scroll para o final, para ver o texto mais recente!
        

    def carregar_regras_firewall(self):
        print(f"Load firewall rules from hos {self.container_id_host_regras_firewall[1]}")

        resposta = messagebox.askyesno("Confirmation","This will overwrite the existing rules in the interface. Are you sure you want to continue?")
        # TODO - na UTPFR deu problema na hora de copiar o arquivo do firewall para o container, ele dizia que copiava e não copiava nada, só copiou quando foi dado um touch no arquivo - ver isso.
        if resposta:
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "cat", "/etc/firewall.sh"]
            result = containers.run_command(command)
            self.text_regras.delete(1.0, tk.END)
            self.text_regras.insert(tk.END, result.stdout)

    # TODO - será que seria bom um botão para zerar as regras de firewall?

    def enviar_executar_arquivos_regras_firewall(self, file_rules, reset): # se for reset indica que o caminho é o arquivo de reset, caso contrário são regras
        print(f"Send and execute firewall rules on host {self.container_id_host_regras_firewall[1]}")
        
        if reset!=None:
            containers.copy_host2container(self.container_id_host_regras_firewall[0], file_rules, "/etc/firewall_reset.sh")
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "sh", "/etc/firewall_reset.sh"]
        else:
            containers.copy_host2container(self.container_id_host_regras_firewall[0], file_rules, "/etc/firewall.sh")
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "sh", "/etc/firewall.sh"]

        result = containers.run_command(command)

        self.text_ativas.delete(1.0, tk.END)
        if result.stderr:
            self.text_ativas.delete(1.0, tk.END)
            self.text_ativas.insert(tk.END, f"\n* Error applying firewall rules - check if there is something wrong with the rules on host {self.container_id_host_regras_firewall[1]}:\n\n")
            self.text_ativas.insert(tk.END, result.stderr)
            self.text_ativas.see(tk.END) # rola o scroll para o final, para ver o texto mais recente!
            messagebox.showinfo("Warning", "Something went wrong while executing the rules, check the output!")
        else:
            self.listar_regras_firewall()
            self.text_ativas.insert(tk.END, f"\n* Firewall status on host {self.container_id_host_regras_firewall[1]} after rules have been applied\n\n")
            self.text_ativas.see(tk.END) # rola o scroll para o final, para ver o texto mais recente!

    def aplicar_regras_firewall(self):
        print(f"Apply rules on the firewall of host {self.container_id_host_regras_firewall[1]}")
        regras = self.text_regras.get("1.0", tk.END)
        file_rules="tmp/regras.sh"
        with open(file_rules, "w", encoding="utf-8") as arquivo:
            arquivo.write(regras)
        print(f"Rules saved in the file {file_rules}")
        if self.reset_firewall.get() == 1: # se checkbox estiver marcado primeiro zera o firewall, depois aplica as regras.
            self.enviar_executar_arquivos_regras_firewall("tmp/reset_firewall.sh", 1)
        
        self.enviar_executar_arquivos_regras_firewall(file_rules, None)
        
        if self.reset_firewall.get() == 1:
            self.text_ativas.insert(tk.END, f"\n>>Warning!<< The firewall rules of host {self.container_id_host_regras_firewall[1]} were reset via the interface, but this SHOULD be in your firewall commands because firewalls do not reset automatically in real life!\n\n")
            self.text_ativas.see(tk.END) # rola o scroll para o final, para ver o texto mais recente!

    def zerar_regras_firewall(self):
        print(f"Reset firewall rules on host {self.container_id_host_regras_firewall[1]}")
        resposta = messagebox.askyesno("Warning","This action of resetting firewall rules does not exist by default, meaning this should be handled in your firewall rules. Are you sure you want to continue?")
        if resposta:
            self.enviar_executar_arquivos_regras_firewall("tmp/reset_firewall.sh", 1)

    def selecionar_tudo(self, event=None):
        """Seleciona todo o texto."""
        self.text.tag_add("sel", "1.0", "end")
        return "break"  # Impede o comportamento padrão do atalho


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
        tabela_portas.heading("Protocolo", text="Protocol")
        tabela_portas.heading("Porta", text="Port")
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
        botao_adicionar = ttk.Button(frame_botoes, text="Add Port", command=lambda: self.adicionar_linha(tabela_portas))
        botao_adicionar.pack(side=tk.LEFT, padx=5)

        # Botão para remover linha
        botao_remover = ttk.Button(frame_botoes, text="Delete Port ", command=lambda: self.remover_linha(tabela_portas))
        botao_remover.pack(side=tk.LEFT, padx=5)

        ttk.Button(popup, text="Reload Ports", command=lambda: self.salvar_portas_em_arquivo(container_id, tabela_portas)).pack(pady=10)

        # Função para adicionar uma nova linha
    def adicionar_linha(self, tabela_portas):
        """Abre uma nova janela para adicionar uma porta à Treeview"""
        popup = tk.Toplevel()
        popup.title("Add Port")
        popup.geometry("300x150")

        # Função para validar e adicionar a porta
        def adicionar_porta():
            protocolo = combo_protocolo.get().strip().upper()
            porta = entry_porta.get().strip()

            # Valida o protocolo
            if protocolo not in ["TCP", "UDP"]:
                messagebox.showerror("Error", "Invalid protocol! Choose TCP or UDP.")
                return

            # Valida a porta
            try:
                porta = int(porta)
                if porta < 1 or porta > 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid port! Must be a number between 0 and 65535.")
                return

            # Verifica se a combinação protocolo/porta já existe na tabela
            for linha in tabela_portas.get_children():
                valores = tabela_portas.item(linha, "values")
                if valores[0].upper() == protocolo and valores[1] == str(porta):
                    messagebox.showerror("Error", f"Port {porta}/{protocolo} already exists in the table!")
                    return

            # Adiciona a nova porta à Treeview
            tabela_portas.insert("", tk.END, values=(protocolo, porta))
            popup.destroy()  # Fecha a janela popup

        # Campo para selecionar o protocolo
        ttk.Label(popup, text="Protocol:").pack(pady=5)
        combo_protocolo = ttk.Combobox(popup, values=["TCP", "UDP"], state="readonly")
        combo_protocolo.set("TCP")  # Valor padrão
        combo_protocolo.pack(pady=5)

        # Campo para inserir a porta
        ttk.Label(popup, text="Port:").pack(pady=5)
        entry_porta = ttk.Entry(popup)
        entry_porta.pack(pady=5)

        # Botão para adicionar a porta
        ttk.Button(popup, text="Add", command=adicionar_porta).pack(pady=10)

    # Função para remover a linha selecionada
    def remover_linha(self, tabela_portas):
        print("Delete")
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
            print(f"Ports successfully saved in file {nome_arquivo}!")
        except Exception as e:
            print(f"Error saving ports: {e}")
        
        # recarrega essas portas no container ligando o sevidor com as novas portas.
        self.reload_ports(containerId, nome_arquivo)
        # reinicia os servidor
        containers.start_server(containerId)

    def reload_ports(self, container_id, nome_arquivo):
        """Salvar as portas abertas (lógica futura)"""
        print(f"Reload ports from {container_id}")

        containers.copy_ports2server(container_id, nome_arquivo)

    def create_firewall_tab(self):
        """Cria a interface para os testes de firewall"""
        ttk.Label(self.firewall_frame, text="Firewall Test", font=("Arial", 12)).pack(pady=10)

        # Frame para os campos de entrada
        frame_entrada = ttk.Frame(self.firewall_frame)
        #frame_entrada.pack(fill="x", padx=10, pady=5)
        frame_entrada.pack(pady=10)

        # Lista de valores exibidos no Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # se não houver elementos apresenta uma mensagem
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]
            messagebox.showerror("Warning", "Something seems to be wrong! \n Is GNS3 or the hosts turned on?")
        # Ordena a lista por ordem crescente
        #self.hosts_display.sort() # TODO - ver se ao ordenar, se acontece algo de estranho nos teste, tal como, dá erro de rede ao enviar TCP/80 do host1 para o host2, mas o contrário não (em um cenário com três hosts), mas no comando direto no host1 funciona normal!

        protocols = ["TCP", "UDP", "ICMP"]

        #configurando stilo - para o readonly não ficar cinza
        style = ttk.Style()
        style.map("TCombobox", fieldbackground=[("readonly", "white")])
        # cor de fundo da linha selecionada - para não tampar a cor do teste


        # Componentes de entrada
        ttk.Label(frame_entrada, text="Source IP:").grid(row=0, column=0)
        self.src_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.src_ip.current(0)
        self.src_ip.grid(row=1, column=0)


        ttk.Label(frame_entrada, text="Destination IP:").grid(row=0, column=1)
        self.dst_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25)
        if len(self.containers_data) > 1: # verifica se há mais que um elemento na lista de hosts, se não houver não dá para setar o segundo como padrão.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

        self.dst_ip.grid(row=1, column=1)
        # Vincula o evento de seleção
        self.dst_ip["state"] = "normal"

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

        # Frame para exibir os testes adicionados
        self.tests_frame = ttk.Frame(self.firewall_frame)
        self.tests_frame.pack(fill="x", padx=10, pady=10)

        # Frame intermediário para centralizar os botões
        self.button_frame = tk.Frame(self.tests_frame)
        self.button_frame.pack(pady=10)  # Centraliza verticalmente

        button_size=15
        # Criando e adicionando os botões dentro do frame intermediário
        self.button_tree_add = tk.Button(self.button_frame, text="Add", command=self.add_entry, width=button_size, underline=0)
        self.button_tree_add.pack(side="left", padx=5)
        self.root.bind("<Alt-a>", lambda event: self.add_entry())

        self.button_tree_edit = tk.Button(self.button_frame, text="Edit", command=self.edit_entry, width=button_size, underline=0)
        self.button_tree_edit.pack(side="left", padx=5)
        # TODO - tem que pensar em quais momentos habilitar e desabilitar os binds, pq da forma que ele está funciona em qualquer lugar!
        #self.root.bind("<Alt-e>", lambda event: self.edit_entry())

        self.button_tree_del = tk.Button(self.button_frame, text="Delete", command=self.delete_entry, width=button_size, underline=0)
        self.button_tree_del.pack(side="left", padx=5)
        #self.root.bind("<Alt-d>", lambda event: self.delete_entry())

        self.button_tree_test = tk.Button(self.button_frame, text="Test Line", command=self.testar_linha_tree, width=button_size, underline=8)
        self.button_tree_test.pack(side="left", padx=5)
        #self.root.bind("<Alt-l>", lambda event: self.testar_linha_tree())

        self.button_tree_test_all = tk.Button(self.button_frame, text="Test All", command=self.executar_todos_testes_thead_tree, width=button_size, underline=0)
        self.button_tree_test_all.pack(side="left", padx=5)
        #self.root.bind("<Alt-l>", lambda event: self.executar_todos_testes())


        # Frame para exibir os testes adicionados na treeview
        self.tests_frame_Tree = ttk.Frame(self.firewall_frame)
        self.tests_frame_Tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.hidden_data = {}  # Dicionário para armazenar Container ID associado ao Teste ID
        self.entries = []
        visible_fields = ["#", "Container ID", "Source", "Destination", "Protocol", "Source Port", "Destination Port", "Expected", "Result", "flow", "data"]
        self.tree = ttk.Treeview(self.tests_frame_Tree, columns=visible_fields, show="headings")

        font = ("TkDefaultFont", 10)
        tk_font = tk.font.Font(font=font)

        self.tree.heading("#", text="#")
        self.tree.column("#", width=30, anchor="e", stretch=False)

        self.colunaContainerID=50 # deixar em zero para essa coluna sumir.
        self.tree.heading("Container ID", text="Container ID")
        self.tree.column("Container ID", width=self.colunaContainerID, stretch=False)

        self.tree.heading("Source", text="Source")
        self.tree.column("Source", width=250, stretch=False)

        self.tree.heading("Destination", text="Destination")
        self.tree.column("Destination", width=250, stretch=False)

        self.tree.heading("Protocol", text="Protocol")
        self.tree.column("Protocol", width=80, anchor="center", stretch=False)

        self.tree.heading("Source Port", text="Src Port")
        self.tree.column("Source Port", width=80, anchor="center", stretch=False)

        self.tree.heading("Destination Port", text="Dst Port")
        self.tree.column("Destination Port", width=80, anchor="center", stretch=False)

        self.tree.heading("Expected", text="Expected")
        self.tree.column("Expected", width=80, anchor="center", stretch=False)

        self.tree.heading("Result", text="Result")
        self.tree.column("Result", width=80, anchor="w", stretch=False)

        self.tree.heading("flow", text="Network Flow")
        self.tree.column("flow", width=200, anchor="w", stretch=False)

        self.tree.heading("data", text="Network Data")
        self.tree.column("data", minwidth=100, width=200, anchor="w", stretch=True)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # TODO - o scroll não esta se ajustando quando os dados superam o tamanho da janela!
        scroll_tree = tk.Scrollbar(self.tests_frame_Tree, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=scroll_tree.set)
        scroll_tree.pack(side="bottom", fill="x")

        # Definição das cores
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[("selected", "#4a90e2")])
        self.tree.tag_configure("yes", background="lightgreen")
        self.tree.tag_configure("yesFail", background="lightblue")
        self.tree.tag_configure("no", background="salmon")
        self.tree.tag_configure("error", background="yellow")
        #self.tree.tag_configure("nat", background="lightblue")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_tree_select_double)
        self.tree.bind('<Escape>', self.on_tree_select)

        btn_frame = tk.Frame(root)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.button_tree_edit.config(state="disabled")
        self.button_tree_del.config(state="disabled")
        self.button_tree_test.config(state="disabled")
        if not self.tree.get_children():
            self.button_tree_test_all.config(state="disabled")

        # Frame legenda
        self.frame_legenda_testes = ttk.LabelFrame(self.firewall_frame, text="Legenda")
        self.frame_legenda_testes.pack(side="bottom", fill="x", padx=20, pady=15)
        self.frame_legenda_testes.pack_propagate(False)
        self.frame_legenda_testes.config(width=700, height=50)

        tk.Label(self.frame_legenda_testes, bg="lightgreen", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Test successfully completed - net flow allowed.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="lightblue", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Test successfully completed - net flow blocked.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="red", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Test failed.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="yellow", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Error (e.g., error in IP, GW, DNS, Server)", font=("Arial", 10)).pack(side="left")

        self.frame_botoes_salvar_testes = ttk.Frame(self.firewall_frame)
        self.frame_botoes_salvar_testes.pack(pady=10)

        self.button_save_tests = ttk.Button(self.frame_botoes_salvar_testes, text="Save Tests", command=self.save_tests)
        self.button_save_tests.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.button_save_tests_as = ttk.Button(self.frame_botoes_salvar_testes, text="Save Tests As", command=self.save_tests_as)
        self.button_save_tests_as.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        self.button_load_tests = ttk.Button(self.frame_botoes_salvar_testes, text="Open Tests", command=self.open_tests)
        self.button_load_tests.grid(row=0, column=5, padx=10, pady=10, sticky="nsew")

    def on_tree_select(self, event):
        print("on_tree_select")
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                #print(f"{item_values}")
                
                self.src_ip.set(item_values[2])

                self.dst_ip.delete(0, tk.END)
                self.dst_ip.insert(0, item_values[3])

                self.protocol.set(item_values[4])

                self.src_port.delete(0, tk.END)
                self.src_port.insert(0, item_values[5])

                self.dst_port.delete(0, tk.END)
                self.dst_port.insert(0, item_values[6])

                self.expected.set(item_values[7])

        if not self.tree.selection():
            self.button_tree_test.config(state="disabled")
        else:
            self.button_tree_test.config(state="normal")
            self.button_tree_test_all.config(state="normal")

        self.button_tree_add.config(state="normal")
        self.button_tree_edit.config(state="disable")
        self.button_tree_del.config(state="disable")
    
    def on_tree_select_double(self, event):
        self.on_tree_select(event)
        self.buttons_edit_state()
        
    def add_entry(self):
        print("add_entry")
        
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.so_validar_e_adicionar_teste() != 0: return # testa os valores

        # Obtém o ID do container selecionado no Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
            print(f"container_data selected_index{selected_index} -  {self.containers_data[selected_index]}")
        else:
            container_id = "N/A"  # Caso nenhum container seja selecionado
        
        row_index = len(self.tree.get_children()) + 1 # indice da linha da tree

        values = [src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        for item in self.tree.get_children(): # evita teste duplicados
            existing_values = self.tree.item(item, "values")
            #print(f"valores existentes\n{values}\n{existing_values[2:]}")
            if tuple(values) == existing_values[2:]:
                #print(f"valores iguais - \n{values}\n{existing_values}")
                messagebox.showwarning("Warning", "This entry already exists in the table!")
                return

        values=[]
        self.tree.insert("", "end", values=[row_index, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "])
        self.tree.column("Container ID", width=self.colunaContainerID, stretch=False)
        
        self.buttons_normal_state()

    # TODO - ver uma forma melhor de deixar os botões de adicionar e editar na tabela, pois ficou meio confuso! (talvez habilitar e desabilitar o edit, conforme algum item na tabela seja selecionado)
    def edit_entry(self):
        """Edita um item existente na Treeview."""
        selected_item = self.tree.selection()
        print(f"Selected item {selected_item}")
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item to edit!")
            return
        
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.so_validar_e_adicionar_teste() != 0: return # testa os valores

        values = [src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        for item in self.tree.get_children(): # evita teste duplicados TODO - colocar isso em um método, pois está duplicado!
            existing_values = self.tree.item(item, "values")
            if tuple(values) == existing_values[2:]:
                messagebox.showwarning("Warning", "This entry already exists in the table!")
                return

        # Obtém o ID do container selecionado no Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
        else:
            container_id = "N/A"  # Caso nenhum container seja selecionado
        
        values=[self.tree.item(selected_item, "values")[0], container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        self.tree.item(selected_item, values=values)
        self.tree.item(selected_item, tags="")  # volta a cor para o padrão
        

        self.buttons_normal_state()

    def buttons_normal_state(self):
        self.tree.selection_set(())
        self.button_tree_add.config(state="normal")
        self.button_tree_edit.config(state="disable")
        self.button_tree_del.config(state="disable")
        self.button_tree_test.config(state="disabled")
        self.button_tree_edit.config(text="Editar")
        if not self.tree.get_children():
            self.button_tree_test_all.config(state="disabled")
        else:
            self.button_tree_test_all.config(state="normal")
        
    def buttons_edit_state(self):
        self.button_tree_edit.config(state="normal")
        self.button_tree_del.config(state="normal")
        self.button_tree_add.config(state="disabled")
        self.button_tree_test.config(state="disabled")
        self.button_tree_test_all.config(state="disabled")
        self.button_tree_edit.config(text="Save Edit")

    def delete_entry(self): # TODO - refazer a enumeração das linhas ao remover um teste
        """Remove um item da Treeview."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item to delete!")
            return
        self.tree.delete(selected_item)

        self.buttons_normal_state() 

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
    
    def so_validar_e_adicionar_teste(self):
        """Valida os campos antes de chamar o método adicionar_editar_teste"""
        # Verifica se os campos obrigatórios estão preenchidos

        if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
            messagebox.showwarning("Mandatory fields", "Please fill in all mandatory fields.")
            return -1
        if not self.dst_port.get().isdigit():
            messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
            return -1
        try:
            porta = int(self.dst_port.get())
            if porta < 1 or porta > 65535:
                messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
                return -1
        except ValueError:
            messagebox.showwarning("Invalid port: conversion error.")
            return -1
        
        if self.dst_ip.get() not in self.hosts_display:
            if self.validar_ip_ou_dominio(self.dst_ip.get()) == False:
                messagebox.showwarning(f"Invalid address", "The address must either: \n1. Be on the list, \n2. Be an IP (8.8.8.8), \n3. Be a domain (www.google.com.br).")
                return -1
            else: # se for fora da lista de hosts do cenário, por enquanto só é possível realizar testes de ping.
                if self.protocol.get() != "ICMP":
                    messagebox.showwarning(f"Invalid protocol", "Unfortunately, in this version, only ICMP (ping) can be used to test external hosts.")
                    return -1
                
        return 0
        # TODO - se for alterado o destino, nesta versão do sistema só pode utilizar o protocolo icmp, não dá para utilizar tcp ou udp, pq o servidor (se existir) não vai reconhecer a mensagem enviada.
        # Se todos os campos estiverem preenchidos, chama o método adicionar_editar_teste
        #self.adicionar_editar_teste()

    def validar_e_adicionar_teste(self):
        """Valida os campos antes de chamar o método adicionar_editar_teste"""
        # Verifica se os campos obrigatórios estão preenchidos

        if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
            messagebox.showwarning("Mandatory fields", "Please fill in all mandatory fields.")
            return
        if not self.dst_port.get().isdigit():
            messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
            return
        try:
            porta = int(self.dst_port.get())
            if porta < 1 or porta > 65535:
                messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
                return
        except ValueError:
            messagebox.showwarning("Invalid port: conversion error.")
            return
        
        if self.dst_ip.get() not in self.hosts_display:
            if self.validar_ip_ou_dominio(self.dst_ip.get()) == False:
                messagebox.showwarning(f"Invalid address", "The address must either: \n1. Be on the list, \n2. Be an IP (8.8.8.8), \n3. Be a domain (www.google.com.br).")
                return
            else: # se for fora da lista de hosts do cenário, por enquanto só é possível realizar testes de ping.
                if self.protocol.get() != "ICMP":
                    messagebox.showwarning(f"Invalid protocol", "Unfortunately, in this version, only ICMP (ping) can be used to test external hosts.")
                    return
        # TODO - se for alterado o destino, nesta versão do sistema só pode utilizar o protocolo icmp, não dá para utilizar tcp ou udp, pq o servidor (se existir) não vai reconhecer a mensagem enviada.
        # Se todos os campos estiverem preenchidos, chama o método adicionar_editar_teste
        self.adicionar_editar_teste()
    
    def atualizar_exibicao_testes_tree(self):
        """Atualiza a exibição dos testes na interface"""
        itens = self.tree.get_children()

        for item in itens:
            self.tree.item(item, tags="")  # Define as tags como uma lista vazia
        # TODO - zerar o resultados na última coluna do treeview!

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
            #print("sem parenteses")
            temp_dst_ip = self.extrair_ip_semParenteses(dst_ip)
            if temp_dst_ip != None:
                dst_ip = temp_dst_ip
            else:
                #print("dominio")
                temp_dst_ip = self.extrair_dominio(dst_ip)
                if temp_dst_ip != None:
                    dst_ip = temp_dst_ip
                else:
                    #print("invalido")
                    print(f"\033[33mCould not extract the destination IP in the interface:\n\tThe destination address must be an IP or domain, such as: 8.8.8.8 or www.google.com.\033[0m")
                    return None
        return dst_ip    
    
    def testar_linha_tree(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            print(f"Items to testing:: {values}")
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values
            
            # se não consegiu extrair o IP de destino digitado pelo usuário para
            dst_ip = self.extrair_destino(dst_ip)
            if dst_ip == None: return
            
            print(f"Test executed - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
                print(f"The return of the command on the host is {result_str}")
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing JSON received from host:", e)
                messagebox.showerror("Error", "Could not get a response from the hosts! \n Is GNS3 or the hosts turned on?")
                result = None
                return

            # TODO - para preencher a linha com a cor tem quem comparar qual era a expectativa do teste
            self.colorir_labels_resultado_tree(expected, result, values, selected_item)
            self.tree.selection_set(())
        

    def colorir_labels_resultado_tree(self, expected, result, values, selected_item):
        # TODO - verificar se todos os casos foram contemplados
        # TODO - melhorar a lógica para verificar erros do usuário - tal como testar uma porta que não está ligada!
        print(values)
        update_values = list(values)
        tag = None

        if result["server_response"] == True: # se o servidor respondeu então colocar sent/receved, caso contrário só Sent - TODO - pode haver caso que ele nem enviou, que seria o caso do erro!
                    update_values[9] = "Sent/Receved" # O pacote só foi enviado mas não houve resposta!
                    update_values[8] = "Pass"
        else:
                    update_values[9] = "Sent" # O pacote só foi enviado mas não houve resposta!
                    update_values[8] = "Fail"

        network_data = result['client_ip']+':'+str(result['client_port'])+'->'+result['server_ip']+':'+str(result['server_port'])+'('+result['protocol']+')'+' - Server response? '+ str(result['server_response'])+ ' - Status: '+result['status_msg']
        update_values[-1] = network_data

        if (result["status"] != '0'):
            # ocorreu um erro , tal como a rede do host não estava configurada.
            print(f"\033[33mThere was an error with the host when sending the packet, such as a misconfigured network - IP, GW, etc.\033[0m")
            update_values[8] = "ERROR"
            update_values[9] = "Not Sent"
            tag = "error"
        elif (result["server_response"] == True and expected == "yes"):
            # teste realizado com sucesso e houve resposta do servidor.
            print(f"\033[32mThe SUCCESS test occurred as expected.\033[0m")
            tag = "yes"
        elif (result["server_response"] == False and expected == "no"):
            # O teste de envio de pacotes falou, mas isso era esperado no teste, então isso é um sucesso!
            print(f"\033[32mThe FAIL test occurred as expected.\033[0m")
            tag = "yesFail"
        else: # TODO - acho que a lógica está errada aqui (verificar os casos possíveis) - é que em cliente.py teve que remover o status=1 pq ele dizia que houve erro em um pacote barrado pelo firewall ou bloqueado!
            print(f"\033[31mThe test did NOT occur as expected.\033[0m")
            tag = "no"


        if "dnat" in result: # o dnat só acontece se tiver resposta do servidor então não precisa do result["server_response"] == True - isso vem do server.py
                print("dnat")
                # houve DNAT
                dnat_data = result["dnat"]
                network_data = result['client_ip']+':'+str(result['client_port'])+'->'+dnat_data['ip']+':'+str(dnat_data['port'])+'('+result['protocol']+')'+' - Server response? '+ str(result['server_response'])+ ' - Status: '+result['status_msg']
                update_values[-1] = network_data
                update_values[9] = "Sent/Receved (DNAT)"
        
        # atualiza a linha do teste
        self.tree.item(selected_item, values=update_values, tags=(tag,))
        
        
    
    def executar_todos_testes_thead_tree(self):
        print("Thread to execute all tests.")
        janela_popup = tk.Toplevel(self.root)
        janela_popup.title("Processing...")
        janela_popup.geometry("300x120")
        janela_popup.resizable(False, False)
        
        status_label = tk.Label(janela_popup, text="Starting...", font=("Arial", 10))
        status_label.pack(pady=10)

        progresso_var = tk.IntVar()
        barra_progresso = ttk.Progressbar(janela_popup, length=250, mode="determinate", variable=progresso_var)
        barra_progresso.pack(pady=5)

        self.tree.selection_set(())
        self.atualizar_exibicao_testes_tree()

        threading.Thread(target=self.executar_todos_testes_tree, args=(janela_popup, progresso_var, status_label), daemon=True).start()
    
    def executar_todos_testes_tree(self, janela_popup, progresso_var, status_label):
        """Executa todos os testes"""
        indice=0
        
        itens = self.tree.get_children()

        total_lista = len(itens)
        for teste in itens:
            values = self.tree.item(teste, "values")
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values
            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")
            
            # se não consegiu extrair o IP de destino digitado pelo usuário para
            dst_ip = self.extrair_destino(dst_ip)
            if dst_ip == None: return

            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing the JSON received from the host:", e)
                messagebox.showerror("Error", "Unable to get a response from the hosts! \n Is GNS3 or the hosts running?")
                result = None
                return

            self.colorir_labels_resultado_tree(expected,result, values, teste)

            indice+=1
            porcentagem_concluida = (indice / total_lista) * 100
            progresso_var.set(porcentagem_concluida)  # Atualiza a barra de progresso
            status_label.config(text=f"Processing... {indice}/{total_lista}")
            

        status_label.config(text="Task completed!")
        progresso_var.set(100)  # Garante que a barra vá até o final
        janela_popup.destroy()


    def start_servers(self):
        """Inicia server.py nos containers"""
        print("start_servers")
        # TODO - controlar se houve erro ao iniciar o servidor e em qual container.
        for container in self.containers_data:
            container_id = container["id"]
            containers.start_server(container_id)

        for cid, btn, label_status in self.lista_btn_onOff:
            #print(f"cid/btn {cid} - {btn}")
                btn.config(image=self.power_icon, text="liga")
                status = self.verificar_servidor_onoff(container_id)
                label_status.config(text=f"Server Status: {status}", font=("Arial", 10))
        


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
            messagebox.showerror("Error", "Unable to get a response from the hosts! \n Is GNS3 or the hosts running?")
        # ordena nomes no combobox
        #self.hosts_display.sort() # TODO - Ao ordenar o nome no host de origem, também tem ordenar - fazer ligação com o id do container, pois está perdendo referência.
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
        self.lista_btn_onOff = []
        row_index = 0  # Linha inicial na grid

        # Carrega os ícones
        self.power_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  # Substitua pelo caminho correto do ícone
        self.power_icon_off = tk.PhotoImage(file="img/system-shutdown-symbolic-off.png")  # Substitua pelo caminho correto do ícone
        status_on_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  # Ícone para servidor ligado
        status_off_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  # Ícone para servidor desligado

        for host in cont:
            print(f"ID: {host['id']}")
            print(f"Nome: {host['nome']}")
            print(f"Hostname: {host['hostname']}")
            print("Interfaces:")

            status = self.verificar_servidor_onoff(host['id'])
            
            
            #status = "Ligado" # TODO - criar função para ver se o status do servidor do host está ligado ou desligado.

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

            if not host['interfaces']:
                # Criando um sub-frame para alinhar interfaces e IPs juntos
                interface_frame = ttk.Frame(frame)
                interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)
                ip_index = 1
                lbl_interface = ttk.Label(interface_frame, text=f"Interface: None or Down", font=("Arial", 10, "bold"))
                lbl_interface.grid(row=0, column=0, sticky="w")

            else:
                for interface in host['interfaces']:
                    print(f"  - Interface: {interface['nome']}")
                    if_name = interface['nome']

                    # Criando um sub-frame para alinhar interfaces e IPs juntos
                    interface_frame = ttk.Frame(frame)
                    interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)

                    # TODO - percebi que o comando ip mostra os IPs da interface mesmo que esta interface esteja desligada DOWN.
                    # Label com o nome da interface
                    lbl_interface = ttk.Label(interface_frame, text=f"Interface: {if_name}", font=("Arial", 10, "bold"))
                    lbl_interface.grid(row=0, column=0, sticky="w")

                    ip_index = 1
                    for ip in interface['ips']:
                        lbl_ip = ttk.Label(interface_frame, text=f"IP: {ip}", font=("Arial", 10))
                        lbl_ip.grid(row=ip_index, column=0, padx=20, sticky="w")
                        ip_index += 1

                    row_index += 2  # Move para a próxima linha no layout

            # Status do servidor
            lbl_status = ttk.Label(interface_frame, text=f"Status from server: {status}", font=("Arial", 10))
            lbl_status.grid(row=ip_index, column=0, padx=5, sticky="w")

            # Botão de Liga/Desliga com ícone
            btn_toggle = ttk.Button(interface_frame, image=self.power_icon, command=lambda cid=container_id: self.toggle_server(cid, btn_toggle))
            btn_toggle.image = self.power_icon  # Mantém a referência para evitar garbage collection
            btn_toggle.grid(row=ip_index, column=1, padx=10, pady=5, sticky="w")
            self.lista_btn_onOff.append((container_id, btn_toggle, lbl_status))
            row_index += 1  # Linha extra para separar os hosts

    # TODO - fazer o botão atualizar o status do servidor do container de ligado para desligado (passar a variável do botão)
    def verificar_servidor_onoff(self, container_id):
        print(f"Check if server is on or off at container {container_id}")
        cmd = 'docker exec '+ container_id+' ps ax | grep "/usr/local/bin/python ./server.py" | grep -v grep'
        result = containers.run_command_shell(cmd)
        if result !="":
            #print("ligado")
            return "on"
        else:
            #print("desligado")
            return "off"

    # Altera na aba de hosts entre ligado e desligado (altera o botão)
    def toggle_server(self, container_id, btn):
        print(f"Toggling server for container ID: {container_id}")  
        # Encontra o botão correspondente na lista e altera a imagem
        for cid, btn, label_status in self.lista_btn_onOff:
            print(f"cid/btn {cid} - {btn}")
            if cid == container_id:
                imagem_atual = btn["image"][0]
                if imagem_atual == str(self.power_icon):
                    print("off")
                    label_status.config()
                    containers.stop_server(container_id)
                    btn.config(image=self.power_icon_off)
                else:
                    print("on")
                    containers.start_server(container_id)
                    btn.config(image=self.power_icon, text="liga")
                status = self.verificar_servidor_onoff(container_id)
                label_status.config(text=f"Server Status: {status}", font=("Arial", 10))
                break

                
    # TODO - a tab host deveria ter um scroll, já que pode ter mais hosts do que cabe na aba!


    def save_tests_as(self):
        """Abre uma janela para salvar os testes em um arquivo JSON."""
        file_path = filedialog.asksaveasfilename(
            title="Save test file",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:  # Se o usuário cancelar, não faz nada
            return

        self.save_file_path = file_path

        #print(f"Salvando testes no arquivo: {self.save_file_path}")
        self.save_tests()

    def save_tests(self):
        """Salva os dados da Treeview em um arquivo JSON."""
        print("Saving tests...")
        if not self.save_file_path:
            self.save_tests_as()
        else:
            items = self.tree.get_children()
            tests_data = []

            for item in items:
                values = self.tree.item(item, "values")
                if values:
                    # Recupera o Container ID oculto
                    #teste_id = values[0]
                    #container_id = self.hidden_data.get(teste_id, "")  
                    teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values

                    # Monta o dicionário e adiciona à lista
                    tests_data.append({
                        "teste_id": teste_id,
                        "container_id": container_id,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "protocol": protocol,
                        "src_port": src_port,
                        "dst_port": dst_port,
                        "expected": expected,
                        "result": result,
                        "flow": dnat,
                        "data": observation
                    })

            # Escreve no arquivo JSON
            with open(self.save_file_path, "w") as f:
                json.dump(tests_data, f, indent=4)

            print(f"Tests successfully saved in file: {self.save_file_path}")

    # TODO - ao carregar tem que verificar se a origem ainda tem o mesmo nome de container - pois se for em máquinas diferentes ou em projetos diferentes do GNS3 - isso vai mudar!
    # TODO - também teria que ver se os IPs ainda batem, pois em termos de aula, normalmente o professor dá o nome da máquina e não o IP, então teria que verificar se os IPs são o mesmo, caso não for teria que atualizar o IP, provavelmente com a interação do usuário caso o host tenha mais que um IP (escolher qual IP é do teste, principalmente se for de destino - na origem isso não vai fazer muita diferença)
    def load_tests(self):
        """Carrega os dados do arquivo JSON para a Treeview."""
        print("Loading tests...")

        if os.path.exists(self.save_file_path):
            with open(self.save_file_path, "r") as f:
                try:
                    tests_data = json.load(f)
                except json.JSONDecodeError:
                    print("Error loading the JSON file.")
                    return

            # Adiciona os itens na Treeview
            for test in tests_data:
                item_id = self.tree.insert("", "end", values=[
                    test["teste_id"], test["container_id"], test["src_ip"], test["dst_ip"], test["protocol"],
                    test["src_port"], test["dst_port"], test["expected"], test["result"], test["flow"], test["data"]
                ])

                # Restaura o Container ID oculto
                #self.hidden_data[test["teste_id"]] = test["container_id"]

                # Aplica a cor conforme o resultado
                #self.apply_row_color(item_id, test["result"])

            print("Tests successfully loaded!")
            self.buttons_normal_state()
        else:
            print("No test files found.")

    def open_tests(self):
        """Abre uma janela para selecionar um arquivo JSON e carrega os testes."""
        file_path = filedialog.askopenfilename(
            title="Open test file",
            filetypes=[("JSON file", "*.json"), ("All files", "*.*")]
        )

        if not file_path:  # Se o usuário cancelar, não faz nada
            return

        self.save_file_path = file_path

        print(f"Loading tests from file: {file_path}")

        self.load_tests()
    
    def confirmar_saida(self):
        if messagebox.askyesno("Confirmation", "Do you really want to exit the program?"):
            self.root.destroy()

# Executando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
