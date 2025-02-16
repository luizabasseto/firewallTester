import tkinter as tk
from tkinter import ttk

def adicionar_valor(event):
    novo_valor = combobox.get().strip()  # Obtém e limpa espaços extras do valor digitado
    if novo_valor and novo_valor not in valores:  # Verifica se já existe na lista
        valores.append(novo_valor)  # Adiciona o valor à lista
        combobox["values"] = valores  # Atualiza o Combobox
    combobox.set("")  # Limpa a entrada do Combobox

# Criando a janela
root = tk.Tk()
root.title("Combobox Dinâmico")

valores = ["Opção 1", "Opção 2", "Opção 3"]  # Lista inicial

# Criando o Combobox (permite entrada de texto)
combobox = ttk.Combobox(root, values=valores)
combobox.pack(pady=10)
combobox.set("Digite ou selecione")

# Associando a tecla "Enter" para adicionar automaticamente ao Combobox
combobox.bind("<Return>", adicionar_valor)

root.mainloop()

