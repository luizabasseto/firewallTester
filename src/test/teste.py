import tkinter as tk
from tkinter import ttk

def on_button_click(button_id):
    print(f"Botão {button_id} clicado!")

root = tk.Tk()

# Cria o Treeview
tree = ttk.Treeview(root, columns=("Nome", "Idade"), show="headings")
tree.heading("Nome", text="Nome")
tree.heading("Idade", text="Idade")
tree.insert("", "end", values=("João", 30))
tree.insert("", "end", values=("Maria", 25))
tree.pack()

# Função para adicionar botões em cada linha
def add_buttons_to_treeview(tree):
    for i, item in enumerate(tree.get_children()):
        # Obtém as coordenadas da linha
        tree.update_idletasks()  # Atualiza o layout do Treeview
        bbox = tree.bbox(item, column="#0")  # Obtém a caixa delimitadora da linha

        if bbox:
            x_offset = 150  # Ajuste conforme necessário
            y_offset = bbox[1]  # Posição Y da linha

            # Cria três botões para cada linha
            button1 = tk.Button(root, text="Botão 1", command=lambda i=i: on_button_click(f"1 - Linha {i+1}"))
            button1.place(in_=tree, x=x_offset, y=y_offset, width=80, height=bbox[3])  # Ajusta a altura do botão

            button2 = tk.Button(root, text="Botão 2", command=lambda i=i: on_button_click(f"2 - Linha {i+1}"))
            button2.place(in_=tree, x=x_offset + 90, y=y_offset, width=80, height=bbox[3])  # Ajusta a altura do botão

            button3 = tk.Button(root, text="Botão 3", command=lambda i=i: on_button_click(f"3 - Linha {i+1}"))
            button3.place(in_=tree, x=x_offset + 180, y=y_offset, width=80, height=bbox[3])  # Ajusta a altura do botão

# Adiciona os botões ao Treeview
add_buttons_to_treeview(tree)

root.mainloop()
