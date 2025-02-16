import tkinter as tk
from tkinter import scrolledtext
import sys
import time
import threading

class PrintRedirector:
    """Redireciona os prints para um widget Tkinter."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Rolagem automática para o final

    def flush(self):
        pass  # Necessário para compatibilidade com sys.stdout

def executar_prints():
    """Função simulando prints em tempo real."""
    for i in range(10):
        print(f"Linha {i+1}: Teste de saída no Tkinter")
        time.sleep(1)

def iniciar_thread():
    """Inicia os prints em uma thread separada para não travar a GUI."""
    thread = threading.Thread(target=executar_prints, daemon=True)
    thread.start()

# Criando a interface
root = tk.Tk()
root.title("Saída do Programa")

# Criando uma área de texto com barra de rolagem
text_area = scrolledtext.ScrolledText(root, width=80, height=20)
text_area.pack(padx=10, pady=10)

# Redirecionando o print para o widget Text
sys.stdout = PrintRedirector(text_area)

# Botão para iniciar os prints
btn_iniciar = tk.Button(root, text="Iniciar Prints", command=iniciar_thread)
btn_iniciar.pack(pady=5)

root.mainloop()

