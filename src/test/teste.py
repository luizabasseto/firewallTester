import tkinter as tk
from tkinter import ttk

# Criando a janela principal
root = tk.Tk()
root.title("Editor de Regras do Firewall")
root.geometry("600x500")

# Frame superior para o título
frame_titulo = tk.Frame(root)
frame_titulo.pack(fill=tk.X)

label_titulo = tk.Label(frame_titulo, text="Editar regras de firewall", font=("Arial", 12, "bold"))
label_titulo.pack(pady=5)

# Criando LabelFrame para as regras a serem aplicadas
frame_regras = ttk.LabelFrame(root, text="Regras a serem aplicadas no firewall")
frame_regras.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

text_regras = tk.Text(frame_regras, wrap=tk.NONE, height=10)
text_regras.grid(row=0, column=0, sticky="nsew")

scroll_y_regras = tk.Scrollbar(frame_regras, orient=tk.VERTICAL, command=text_regras.yview)
scroll_y_regras.grid(row=0, column=1, sticky="ns")
text_regras.config(yscrollcommand=scroll_y_regras.set)

scroll_x_regras = tk.Scrollbar(frame_regras, orient=tk.HORIZONTAL, command=text_regras.xview)
scroll_x_regras.grid(row=1, column=0, sticky="ew")
text_regras.config(xscrollcommand=scroll_x_regras.set)

frame_regras.grid_columnconfigure(0, weight=1)
frame_regras.grid_rowconfigure(0, weight=1)

# Criando LabelFrame para as regras ativas no firewall (inicialmente oculto)
frame_ativas = ttk.LabelFrame(root, text="Regras ativas no firewall")
frame_ativas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
frame_ativas.pack_forget()  # Escondendo inicialmente

def toggle_frame_ativas():
    if frame_ativas.winfo_ismapped():
        frame_ativas.pack_forget()
    else:
        frame_ativas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

text_ativas = tk.Text(frame_ativas, wrap=tk.NONE, height=10)
text_ativas.grid(row=0, column=0, sticky="nsew")

scroll_y_ativas = tk.Scrollbar(frame_ativas, orient=tk.VERTICAL, command=text_ativas.yview)
scroll_y_ativas.grid(row=0, column=1, sticky="ns")
text_ativas.config(yscrollcommand=scroll_y_ativas.set)

scroll_x_ativas = tk.Scrollbar(frame_ativas, orient=tk.HORIZONTAL, command=text_ativas.xview)
scroll_x_ativas.grid(row=1, column=0, sticky="ew")
text_ativas.config(xscrollcommand=scroll_x_ativas.set)

frame_ativas.grid_columnconfigure(0, weight=1)
frame_ativas.grid_rowconfigure(0, weight=1)

# Criando os botões
frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=10)

btn_aplicar = tk.Button(frame_botoes, text="Aplicar Regras")
btn_aplicar.pack(side=tk.LEFT, padx=10)

btn_ver_ativas = tk.Button(frame_botoes, text="Ver Regras Ativas", command=toggle_frame_ativas)
btn_ver_ativas.pack(side=tk.RIGHT, padx=10)

# Rodando a interface
tk.mainloop()

