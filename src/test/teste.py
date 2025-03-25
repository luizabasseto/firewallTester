import tkinter as tk
from tkinter import ttk

janela = tk.Tk()
janela.title("Treeview com Scrollbars (pack)")

frame_tree = ttk.Frame(janela) # Frame para a Treeview e barra de rolagem vertical
frame_tree.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame_tree, columns=('Coluna 1', 'Coluna 2', 'Coluna 3'))
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

barra_vertical = ttk.Scrollbar(frame_tree, orient='vertical', command=tree.yview)
barra_vertical.pack(side=tk.RIGHT, fill=tk.Y)

frame_horizontal = ttk.Frame(janela) # Frame para a barra de rolagem horizontal
frame_horizontal.pack(fill=tk.X)

barra_horizontal = ttk.Scrollbar(frame_horizontal, orient='horizontal', command=tree.xview)
barra_horizontal.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

tree.configure(yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set)

tree.heading('#0', text='Item')
tree.heading('Coluna 1', text='Valor 1')
tree.heading('Coluna 2', text='Valor 2')
tree.heading('Coluna 3', text='Valor 3')

for i in range(50):
    tree.insert('', 'end', text=f'Item {i}', values=(f'Valor 1.{i}', f'Valor 2.{i}', f'Valor 3.{i}'))

janela.mainloop()
