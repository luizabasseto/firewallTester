import tkinter as tk
from tkinter import ttk, messagebox

def is_duplicate(values):
    """Verifica se os valores já existem na Treeview."""
    for item in tree.get_children():
        existing_values = tree.item(item, "values")  # Obtem os valores existentes
        if tuple(values) == existing_values:  # Comparação correta com tupla
            return True  
    return False  

def add_entry():
    values = [entry.get().strip() for entry in entries]  # Remove espaços extras

    if not all(values):
        messagebox.showwarning("Atenção", "Todos os campos devem ser preenchidos!")
        return

    if is_duplicate(values):  # Verifica duplicatas antes de adicionar
        messagebox.showwarning("Atenção", "Essa entrada já existe na tabela!")
        return

    item_id = tree.insert("", "end", values=values)
    apply_row_color(item_id, values[-1])  # Aplica cor conforme resultado
    clear_entries()

def apply_row_color(item_id, result):
    """Aplica cor na linha conforme o valor de Result."""
    if result.lower() == "yes":
        tree.item(item_id, tags=("yes",))
    elif result.lower() == "no":
        tree.item(item_id, tags=("no",))

def clear_entries():
    """Limpa os campos de entrada."""
    for entry in entries:
        entry.delete(0, tk.END)

# Criar janela
root = tk.Tk()
root.title("Treeview sem duplicatas")

# Criar campos de entrada
fields = ["Teste ID", "IP Source", "IP Destination", "Protocol", "Source Port", "Destination Port", "Expected", "Result"]
entries = []

frame = tk.Frame(root)
frame.pack(pady=10)

for i, field in enumerate(fields):
    tk.Label(frame, text=field).grid(row=i, column=0, padx=5, pady=2, sticky='e')
    entry = tk.Entry(frame)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

# Criar Treeview
tree = ttk.Treeview(root, columns=fields, show="headings")
for field in fields:
    tree.heading(field, text=field)
    tree.column(field, width=100)
tree.pack(pady=10)

# Definir estilos de cores
style = ttk.Style()
tree.tag_configure("yes", background="lightgreen")
tree.tag_configure("no", background="salmon")

# Botões
btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Adicionar", command=add_entry).grid(row=0, column=0, padx=5)

tk.Button(root, text="Sair", command=root.quit).pack(pady=10)

root.mainloop()
