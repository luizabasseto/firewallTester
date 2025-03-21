import tkinter as tk
import tkinter.ttk as ttk

def mostrar_portas():
    """Exibe as portas no Treeview."""

    # Dados de exemplo (substitua por suas portas reais)
    portas_lista = [
        {"protocolo": "tcp", "numero": "80", "status": "aberta"},
        {"protocolo": "tcp", "numero": "443", "status": "aberta"},
        {"protocolo": "udp", "numero": "53", "status": "aberta"},
        {"protocolo": "tcp", "numero": "22", "status": "fechada"},
    ]

    # Cria a janela popup
    popup = tk.Toplevel(root)
    popup.title("Portas do Container")

    # Define as colunas do Treeview
    colunas = ("Protocolo", "Número", "Status")
    ports_treeview = ttk.Treeview(popup, columns=colunas, show="headings")

    # Define os cabeçalhos das colunas
    for col in colunas:
        ports_treeview.heading(col, text=col)

    # Insere as portas no Treeview
    for porta in portas_lista:
        ports_treeview.insert("", tk.END, values=(porta["protocolo"], porta["numero"], porta["status"]))

    # Posiciona o Treeview na janela
    ports_treeview.pack(pady=5)

# Cria a janela principal
root = tk.Tk()
root.title("Exemplo Treeview")

# Botão para mostrar as portas
botao_mostrar = ttk.Button(root, text="Mostrar Portas", command=mostrar_portas)
botao_mostrar.pack(pady=10)

root.mainloop()
