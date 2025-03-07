import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Texto com Scrollbars")

        # Frame principal para conter o Text e as Scrollbars
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        # Widget Text para edição de texto
        self.text = tk.Text(self.frame, wrap="none")  # wrap="none" permite rolagem horizontal
        self.text.pack(side="left", fill="both", expand=True)

        # Scrollbar vertical
        self.scrollbar_vertical = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.scrollbar_vertical.pack(side="right", fill="y")

        # Scrollbar horizontal
        self.scrollbar_horizontal = ttk.Scrollbar(root, orient="horizontal", command=self.text.xview)
        self.scrollbar_horizontal.pack(side="bottom", fill="x")

        # Configurar o Text para usar as Scrollbars
        self.text.configure(yscrollcommand=self.scrollbar_vertical.set, xscrollcommand=self.scrollbar_horizontal.set)

        # Adicionar algum texto inicial (opcional)
        self.text.insert("1.0", "Este é um exemplo de área de edição de texto com barras de rolagem.\n" * 100)

root = tk.Tk()
app = App(root)
root.mainloop()
