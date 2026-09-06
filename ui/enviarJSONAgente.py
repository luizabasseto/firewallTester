import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("AGENT_API_URL")


def ask_to_agent(*ask, file_paths=None):

    payload = {
        "chatInput": ask[0] if ask else "",
        "type": "construt",
        "sessionId": "sessao-luiza-001"
    }

    print("Trying to talk with o servidor...")

    try:
        if file_paths:

            files = []
            arquivos_abertos = []

            try:
                for caminho in file_paths:

                    if not os.path.exists(caminho):
                        print(f"Aviso: arquivo não encontrado: {caminho}")
                        continue

                    arquivo = open(caminho, "rb")
                    arquivos_abertos.append(arquivo)

                    nome = os.path.basename(caminho)

                    extensao = os.path.splitext(nome)[1].lower()

                    if extensao == ".pdf":
                        mime_type = "application/pdf"

                    elif extensao == ".json":
                        mime_type = "application/json"

                    elif extensao == ".txt":
                        mime_type = "text/plain"

                    else:
                        mime_type = "application/octet-stream"

                    files.append(
                        (
                            "arquivo_enviado",
                            (nome, arquivo, mime_type)
                        )
                    )

                if not files:
                    return "Nenhum arquivo válido foi encontrado."

                response = requests.post(
                    API_URL,
                    data=payload,
                    files=files,
                    timeout=2000
                )

            finally:
                for arquivo in arquivos_abertos:
                    arquivo.close()

        else:

            response = requests.post(
                API_URL,
                json=payload,
                timeout=60
            )
        if response.status_code == 200:

            dados = response.json()

            if isinstance(dados, list):
                dados = dados[0]

            resposta_final = dados.get(
                "output",
                'A IA processou, mas o campo "output" não foi encontrado.'
            )

            return resposta_final

        elif response.status_code == 404:

            return (
                "Erro 404: Webhook não encontrado. "
                "Verifique se o Workflow está ATIVO (Published) no n8n."
            )

        else:

            return (
                f"Erro no servidor ({response.status_code}): "
                f"{response.text}"
            )

    except requests.exceptions.ConnectionError:

        return (
            "Falha técnica: Não foi possível conectar ao servidor. "
            "O túnel do VS Code (porta 5678) está ativo?"
        )

    except Exception as e:

        return f"Erro inesperado: {str(e)}"


if __name__ == "__main__":

    pergunta = (
        "Baseado nos arquivos enviados, crie regras de firewall "
        "que atendam a todo o cenário descrito. "
        "Gere um arquivo JSON com as regras e me retorne "
        "o conteúdo do arquivo JSON."
    )

    arquivos = [
        "/home/luiza/Área de trabalho/Projetos/firewallTester/ui/Atividade-firewallIPtables.pdf",

        "/home/luiza/Área de trabalho/Projetos/firewallTester/topologia_extraida.json"
    ]

    retorno = ask_to_agent(
        pergunta,
        file_paths=arquivos
    )

    print(f"\nAnswer:\n{retorno}")
