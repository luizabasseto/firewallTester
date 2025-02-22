import tkinter as tk
from tkinter import ttk, messagebox

# Função para adicionar uma porta e protocolo à tabela
def adicionar_porta():
    protocolo = entrada_protocolo.get()
    porta = entrada_porta.get()
    if protocolo and porta:
        tabela_portas.insert("", tk.END, values=(protocolo, porta))
        entrada_protocolo.delete(0, tk.END)  # Limpa o campo de protocolo
        entrada_porta.delete(0, tk.END)      # Limpa o campo de porta
    else:
        messagebox.showwarning("Campo vazio", "Por favor, preencha ambos os campos.")

# Função para remover um item selecionado da tabela
def remover_porta():
    item_selecionado = tabela_portas.selection()
    if item_selecionado:
        tabela_portas.delete(item_selecionado)
    else:
        messagebox.showwarning("Nada selecionado", "Por favor, selecione um item para remover.")

# Configuração da janela principal
janela = tk.Tk()
janela.title("Gerenciador de Portas e Protocolos")

# Frame para os campos de entrada
frame_entrada = ttk.Frame(janela)
frame_entrada.pack(pady=10)

# Campo de entrada para protocolo
ttk.Label(frame_entrada, text="Protocolo:").grid(row=0, column=0, padx=5, pady=5)
entrada_protocolo = ttk.Entry(frame_entrada, width=15)
entrada_protocolo.grid(row=0, column=1, padx=5, pady=5)

# Campo de entrada para porta
ttk.Label(frame_entrada, text="Porta:").grid(row=0, column=2, padx=5, pady=5)
entrada_porta = ttk.Entry(frame_entrada, width=15)
entrada_porta.grid(row=0, column=3, padx=5, pady=5)

# Botão para adicionar à tabela
ttk.Button(frame_entrada, text="Adicionar", command=adicionar_porta).grid(row=0, column=4, padx=5, pady=5)

# Tabela para exibir as portas e protocolos
colunas = ("Protocolo", "Porta")
tabela_portas = ttk.Treeview(janela, columns=colunas, show="headings", selectmode="browse")
tabela_portas.heading("Protocolo", text="Protocolo")
tabela_portas.heading("Porta", text="Porta")
tabela_portas.column("Protocolo", width=150, anchor=tk.CENTER)
tabela_portas.column("Porta", width=100, anchor=tk.CENTER)
tabela_portas.pack(pady=10)

# Botão para remover item selecionado
ttk.Button(janela, text="Remover Selecionado", command=remover_porta).pack(pady=5)

# Iniciar a interface
janela.mainloop()