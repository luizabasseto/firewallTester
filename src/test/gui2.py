import tkinter as tk
from tkinter import ttk
import uuid  # Para gerar IDs únicos

class PlanilhaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planilha de Testes")

        # Lista para armazenar os dados adicionados
        self.dados = []

        # Frame para os campos de entrada
        self.frame_entrada = tk.Frame(root)
        self.frame_entrada.pack(pady=10)

        # Componentes de entrada
        self.label_ip_source = tk.Label(self.frame_entrada, text="IP Source:")
        self.label_ip_source.grid(row=0, column=0, padx=5, pady=5)
        self.combo_ip_source = ttk.Combobox(self.frame_entrada, values=["192.168.1.1", "192.168.1.2", "192.168.1.3"])
        self.combo_ip_source.grid(row=0, column=1, padx=5, pady=5)

        self.label_ip_dest = tk.Label(self.frame_entrada, text="IP Destination:")
        self.label_ip_dest.grid(row=0, column=2, padx=5, pady=5)
        self.combo_ip_dest = ttk.Combobox(self.frame_entrada, values=["192.168.1.10", "192.168.1.20", "192.168.1.30"])
        self.combo_ip_dest.grid(row=0, column=3, padx=5, pady=5)

        self.label_protocol = tk.Label(self.frame_entrada, text="Protocol:")
        self.label_protocol.grid(row=0, column=4, padx=5, pady=5)
        self.entry_protocol = tk.Entry(self.frame_entrada)
        self.entry_protocol.grid(row=0, column=5, padx=5, pady=5)

        self.label_source_port = tk.Label(self.frame_entrada, text="Source Port:")
        self.label_source_port.grid(row=0, column=6, padx=5, pady=5)
        self.entry_source_port = tk.Entry(self.frame_entrada)
        self.entry_source_port.grid(row=0, column=7, padx=5, pady=5)

        self.label_dest_port = tk.Label(self.frame_entrada, text="Destination Port:")
        self.label_dest_port.grid(row=0, column=8, padx=5, pady=5)
        self.entry_dest_port = tk.Entry(self.frame_entrada)
        self.entry_dest_port.grid(row=0, column=9, padx=5, pady=5)

        self.label_sucesso = tk.Label(self.frame_entrada, text="Sucesso Esperado:")
        self.label_sucesso.grid(row=0, column=10, padx=5, pady=5)
        self.radio_sucesso = tk.StringVar(value="Sim")
        self.radio_sim = tk.Radiobutton(self.frame_entrada, text="Sim", variable=self.radio_sucesso, value="Sim")
        self.radio_sim.grid(row=0, column=11, padx=5, pady=5)
        self.radio_nao = tk.Radiobutton(self.frame_entrada, text="Não", variable=self.radio_sucesso, value="Não")
        self.radio_nao.grid(row=0, column=12, padx=5, pady=5)

        # Botão para adicionar/editar dados
        self.botao_adicionar = tk.Button(root, text="Adicionar", command=self.adicionar_editar_dados)
        self.botao_adicionar.pack(pady=10)

        # Botão para executar todos os testes
        self.botao_executar_todos = tk.Button(root, text="Executar Testes", command=self.executar_todos_testes)
        self.botao_executar_todos.pack(pady=10)

        # Frame para exibir os dados adicionados
        self.frame_dados = tk.Frame(root)
        self.frame_dados.pack(pady=10)

        # Variável para armazenar o índice do item sendo editado
        self.indice_edicao = None

    def adicionar_editar_dados(self):
        # Coletar os dados dos campos
        ip_source = self.combo_ip_source.get()
        ip_dest = self.combo_ip_dest.get()
        protocol = self.entry_protocol.get()
        source_port = self.entry_source_port.get()
        dest_port = self.entry_dest_port.get()
        sucesso = self.radio_sucesso.get()

        if self.indice_edicao is not None:
            # Editar o item existente, mantendo o ID original
            teste_id = self.dados[self.indice_edicao][0]  # Mantém o ID original
            self.dados[self.indice_edicao] = (teste_id, ip_source, ip_dest, protocol, source_port, dest_port, sucesso)
            self.indice_edicao = None
            self.botao_adicionar.config(text="Adicionar")
        else:
            # Adicionar novo item com um ID único
            teste_id = str(uuid.uuid4())  # Gera um ID único
            self.dados.append((teste_id, ip_source, ip_dest, protocol, source_port, dest_port, sucesso))

        # Limpar os campos de entrada
        self.combo_ip_source.set("")
        self.combo_ip_dest.set("")
        self.entry_protocol.delete(0, tk.END)
        self.entry_source_port.delete(0, tk.END)
        self.entry_dest_port.delete(0, tk.END)
        self.radio_sucesso.set("Sim")

        # Atualizar a exibição dos dados
        self.atualizar_exibicao()

    def atualizar_exibicao(self):
        # Limpar o frame de dados
        for widget in self.frame_dados.winfo_children():
            widget.destroy()

        # Exibir os dados adicionados
        for i, dado in enumerate(self.dados):
            teste_id, ip_source, ip_dest, protocol, source_port, dest_port, sucesso = dado

            # Frame para cada linha de dados
            frame_linha = tk.Frame(self.frame_dados)
            frame_linha.pack(fill=tk.X, pady=2)

            # Exibir cada campo em uma linha
            tk.Label(frame_linha, text=f"ID: {teste_id}").pack(side=tk.LEFT, padx=5)
            tk.Label(frame_linha, text=f"IP Source: {ip_source}").pack(side=tk.LEFT, padx=5)
            tk.Label(frame_linha, text=f"IP Dest: {ip_dest}").pack(side=tk.LEFT, padx=5)
            tk.Label(frame_linha, text=f"Protocol: {protocol}").pack(side=tk.LEFT, padx=5)
            tk.Label(frame_linha, text=f"Source Port: {source_port}").pack(side=tk.LEFT, padx=5)
            tk.Label(frame_linha, text=f"Dest Port: {dest_port}").pack(side=tk.LEFT, padx=5)
            tk.Label(frame_linha, text=f"Sucesso: {sucesso}").pack(side=tk.LEFT, padx=5)

            # Botões de testar, editar e excluir
            botao_testar = tk.Button(frame_linha, text="Testar", command=lambda idx=i: self.testar_linha(idx))
            botao_testar.pack(side=tk.LEFT, padx=5)

            botao_editar = tk.Button(frame_linha, text="Editar", command=lambda idx=i: self.editar_dados(idx))
            botao_editar.pack(side=tk.LEFT, padx=5)

            botao_excluir = tk.Button(frame_linha, text="Excluir", command=lambda idx=i: self.excluir_dados(idx))
            botao_excluir.pack(side=tk.LEFT, padx=5)

    def editar_dados(self, indice):
        # Preencher os campos de entrada com os dados do item selecionado
        _, ip_source, ip_dest, protocol, source_port, dest_port, sucesso = self.dados[indice]
        self.combo_ip_source.set(ip_source)
        self.combo_ip_dest.set(ip_dest)
        self.entry_protocol.delete(0, tk.END)
        self.entry_protocol.insert(0, protocol)
        self.entry_source_port.delete(0, tk.END)
        self.entry_source_port.insert(0, source_port)
        self.entry_dest_port.delete(0, tk.END)
        self.entry_dest_port.insert(0, dest_port)
        self.radio_sucesso.set(sucesso)

        # Armazenar o índice do item sendo editado
        self.indice_edicao = indice
        self.botao_adicionar.config(text="Salvar Edição")

    def excluir_dados(self, indice):
        # Remover o item da lista
        self.dados.pop(indice)
        # Atualizar a exibição dos dados
        self.atualizar_exibicao()

    def testar_linha(self, indice):
        # Criar um objeto com os dados da linha selecionada
        teste_id, ip_source, ip_dest, protocol, source_port, dest_port, sucesso = self.dados[indice]
        teste = {
            "id": teste_id,
            "ip_source": ip_source,
            "ip_dest": ip_dest,
            "protocol": protocol,
            "source_port": source_port,
            "dest_port": dest_port,
            "sucesso": sucesso
        }
        print("Teste executado para a linha:", teste)  # Exemplo de ação (substitua pelo seu código)

    def executar_todos_testes(self):
        # Criar um objeto com todos os testes
        todos_testes = []
        for dado in self.dados:
            teste_id, ip_source, ip_dest, protocol, source_port, dest_port, sucesso = dado
            teste = {
                "id": teste_id,
                "ip_source": ip_source,
                "ip_dest": ip_dest,
                "protocol": protocol,
                "source_port": source_port,
                "dest_port": dest_port,
                "sucesso": sucesso
            }
            todos_testes.append(teste)
        print("Todos os testes executados:", todos_testes)  # Exemplo de ação (substitua pelo seu código)

# Iniciar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = PlanilhaApp(root)
    root.mainloop()
