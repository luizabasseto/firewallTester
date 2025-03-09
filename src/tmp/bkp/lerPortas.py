def ler_portas_protocolos(nome_arquivo):
    """
    Lê um arquivo com tuplas porta/protocolo (uma por linha) e retorna uma lista de tuplas.

    Args:
        nome_arquivo (str): O nome do arquivo a ser lido.

    Returns:
        list: Uma lista de tuplas (porta, protocolo) ou None em caso de erro.
    """
    try:
        with open(nome_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()

        tuplas = []
        for linha in linhas:
            linha = linha.strip()  # Remove espaços em branco extras
            if linha: # Verifica se a linha não está vazia
                try:
                    porta_proto = linha.split('/')
                    if len(porta_proto) == 2:
                        porta = int(porta_proto[0])
                        protocolo = porta_proto[1].lower() # Converte para maiúsculo para consistência
                        tuplas.append((porta, protocolo))
                    else:
                        print(f"Erro: Linha inválida: '{linha}'. Formato deve ser porta/protocolo.")

                except ValueError:
                    print(f"Erro: Porta inválida na linha: '{linha}'. Deve ser um número inteiro.")

        return tuplas

    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        return None

# Exemplo de uso:
nome_arquivo = "conf/portas.conf"  # Substitua pelo nome do seu arquivo
tuplas = ler_portas_protocolos(nome_arquivo)

if tuplas:
    print("Tuplas lidas do arquivo:")
    for porta, protocolo in tuplas:
        print(f"Porta: {porta}, Protocolo: {protocolo}")

    # Exemplo de como acessar os dados individualmente:
    for porta, protocolo in tuplas:
        # Faça algo com a porta e o protocolo...
        if protocolo == "TCP":
            print(f"Porta TCP: {porta}")
        elif protocolo == "UDP":
            print(f"Porta UDP: {porta}")

else:
    print("Não foi possível ler as portas e protocolos do arquivo.")
