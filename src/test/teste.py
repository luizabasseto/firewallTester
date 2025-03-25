import tkinter as tk
from tkinter import ttk

class SuaClasse:
    def __init__(self, root):
        self.root = root
        self.create_hosts_tab()

    def create_hosts_tab(self):
        """
        Cria a aba Hosts, centralizando todas as informações no meio da tela.
        """

        # Frame principal que ocupa toda a tela
        self.hosts_frame = tk.Frame(self.root)
        self.hosts_frame.pack(fill=tk.BOTH, expand=True)

        # Criando um frame intermediário para centralizar tudo
        self.central_frame = tk.Frame(self.hosts_frame)
        self.central_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(self.central_frame, text="Network Containers Hosts:", font=("Arial", 14)).pack(pady=10)

        # Botão para ligar os servidores
        ttk.Button(self.central_frame, text="Turn on servers", command=self.hosts_start_servers).pack(pady=5)

        # Criando um Canvas para permitir rolagem se necessário
        self.frame_all_hosts = tk.Frame(self.central_frame)
        self.frame_all_hosts.pack(fill=tk.BOTH, expand=True, pady=10)

        self.canva_hosts = tk.Canvas(self.frame_all_hosts, width=400, height=300)
        self.canva_hosts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.frame_all_hosts, orient="vertical", command=self.canva_hosts.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canva_hosts.configure(yscrollcommand=scrollbar.set)

        # Frame interno dentro do Canvas
        self.frame_conteudo_hosts = ttk.Frame(self.canva_hosts)
        self.canva_hosts.create_window((0, 0), window=self.frame_conteudo_hosts, anchor="n")

        # Atualiza o tamanho da área de rolagem quando necessário
        self.frame_conteudo_hosts.bind("<Configure>", lambda e: self.canva_hosts.configure(scrollregion=self.canva_hosts.bbox("all")))

        self.hosts_show_host_informations_in_host_tab()

    def hosts_start_servers(self):
        print("Iniciando servidores...")

    def hosts_show_host_informations_in_host_tab(self):
        """Adiciona frames dinamicamente ao centro da tela."""

        for i in range(10):  # Reduzido para 10 só para facilitar o teste
            frame_item = ttk.Frame(self.frame_conteudo_hosts, padding=10, borderwidth=2, relief="groove")
            frame_item.pack(fill=tk.X, padx=20, pady=5)

            label = ttk.Label(frame_item, text=f"Host {i+1}")
            label.pack(side=tk.LEFT, padx=10)

            botao = ttk.Button(frame_item, text=f"Config {i+1}")
            botao.pack(side=tk.RIGHT, padx=10)

# Criando a janela principal
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Interface Centralizada")
    root.geometry("800x600")  # Define um tamanho inicial maior para melhor visualização

    app = SuaClasse(root)

    root.mainloop()

