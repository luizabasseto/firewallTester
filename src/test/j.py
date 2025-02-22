import tkinter as tk

def mostrar_legenda():
    """Abre uma nova janela com as legendas."""
    # Cria a janela de legenda
    legenda_window = tk.Toplevel(root)
    legenda_window.title("Legenda")
    legenda_window.geometry("300x150")

    # Quadrado verde: Teste realizado com sucesso
    frame_verde = tk.Frame(legenda_window)
    frame_verde.pack(pady=5, padx=10, anchor="w")
    tk.Label(frame_verde, bg="green", width=5, height=2).pack(side="left", padx=5)  # Quadrado verde
    tk.Label(frame_verde, text="Teste realizado com sucesso").pack(side="left")

    # Quadrado vermelho: Teste não realizado com sucesso
    frame_vermelho = tk.Frame(legenda_window)
    frame_vermelho.pack(pady=5, padx=10, anchor="w")
    tk.Label(frame_vermelho, bg="red", width=5, height=2).pack(side="left", padx=5)  # Quadrado vermelho
    tk.Label(frame_vermelho, text="Teste não realizado com sucesso").pack(side="left")

    # Quadrado amarelo: Ocorreu alguma falha durante o teste
    frame_amarelo = tk.Frame(legenda_window)
    frame_amarelo.pack(pady=5, padx=10, anchor="w")
    tk.Label(frame_amarelo, bg="yellow", width=5, height=2).pack(side="left", padx=5)  # Quadrado amarelo
    tk.Label(frame_amarelo, text="Ocorreu alguma falha durante o teste").pack(side="left")

# Cria a janela principal
root = tk.Tk()
root.title("Interface com Legenda")
root.geometry("300x100")

# Botão para mostrar a legenda
botao_legenda = tk.Button(root, text="Mostrar Legenda", command=mostrar_legenda)
botao_legenda.pack(pady=20)

# Inicia o loop principal da interface
root.mainloop()
