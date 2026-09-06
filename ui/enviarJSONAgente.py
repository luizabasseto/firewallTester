import argparse
import os
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("AGENT_API_URL")


TIPOS_VALIDOS = {
    "validar_regras": ["pdf", "regras", "rede"],
    "sugerir_testes": ["rede", "regras"],
    "sugerir_regras": ["rede", "pdf"],
}

ENV_VAR_POR_ARQUIVO = {
    "pdf": "FIREWALL_PDF_PATH",
    "regras": "REGRAS_JSON_PATH",
    "rede": "TOPOLOGIA_JSON_PATH",
}

MIME_POR_EXTENSAO = {
    ".pdf": "application/pdf",
    ".json": "application/json",
    ".txt": "text/plain",
    ".sh": "application/x-sh",
}

def ask_to_agent(chat_input, tipo, session_id, file_paths=None):

    payload = {
        "chatInput": chat_input,
        "type": tipo,
        "sessionId": session_id,
    }

    print(f"Enviando requisição (type={tipo}, sessionId={session_id})...")

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
                    mime_type = MIME_POR_EXTENSAO.get(
                        extensao, "application/octet-stream"
                    )

                    files.append(("arquivo_enviado", (nome, arquivo, mime_type)))

                if not files:
                    return "Nenhum arquivo válido foi encontrado."

                response = requests.post(
                    API_URL, data=payload, files=files, timeout=2000
                )

            finally:
                for arquivo in arquivos_abertos:
                    arquivo.close()

        else:
            response = requests.post(API_URL, json=payload, timeout=60)

        if response.status_code == 200:
            dados = response.json()

            if isinstance(dados, list):
                dados = dados[0]

            return dados.get(
                "output", 'A IA processou, mas o campo "output" não foi encontrado.'
            )

        elif response.status_code == 404:
            return (
                "Erro 404: Webhook não encontrado. "
                "Verifique se o Workflow está ATIVO (Published) no n8n."
            )

        else:
            return f"Erro no servidor ({response.status_code}): {response.text}"

    except requests.exceptions.ConnectionError:
        return (
            "Falha técnica: Não foi possível conectar ao servidor. "
            "Verifique se o n8n está ativo e acessível na URL configurada."
        )

    except Exception as e:
        return f"Erro inesperado: {str(e)}"


def resolver_caminho(chave, valor_arg):

    if valor_arg:
        return valor_arg
    return os.getenv(ENV_VAR_POR_ARQUIVO[chave])


def montar_lista_arquivos(tipo, args):
    chaves_necessarias = TIPOS_VALIDOS[tipo]
    caminhos = {}

    for chave in chaves_necessarias:
        valor_arg = getattr(args, chave)
        caminho = resolver_caminho(chave, valor_arg)
        if not caminho:
            raise SystemExit(
                f"Faltou o arquivo '{chave}' para o tipo '{tipo}'. "
                f"Informe via --{chave} ou defina {ENV_VAR_POR_ARQUIVO[chave]} no .env."
            )
        caminhos[chave] = caminho

    return list(caminhos.values())


PERGUNTAS_PADRAO = {
    "validar_regras": (
        "Baseado no PDF da atividade, nas regras criadas e no cenário de rede, "
        "verifique se as regras atendem aos requisitos. Aponte o que está "
        "correto e o que está faltando ou incorreto."
    ),
    "sugerir_testes": (
        "Baseado no cenário de rede e nas regras criadas, sugira testes "
        "que validem se o firewall está se comportando como esperado."
    ),
    "sugerir_regras": (
        "Baseado no cenário de rede e no enunciado da atividade, sugira "
        "regras de firewall que atendam aos requisitos descritos."
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description="Envia arquivos e uma pergunta para o agente de IA no n8n."
    )
    parser.add_argument(
        "tipo",
        choices=list(TIPOS_VALIDOS.keys()),
        help="Qual função do agente executar.",
    )
    parser.add_argument("--pdf", help="Caminho do PDF da atividade.")
    parser.add_argument("--regras", help="Caminho do JSON com as regras criadas.")
    parser.add_argument("--rede", help="Caminho do JSON com o cenário de rede.")
    parser.add_argument(
        "--pergunta", help="Pergunta customizada (opcional; há um padrão por tipo)."
    )
    parser.add_argument(
        "--session-id",
        help=(
            "ID de sessão a reaproveitar (para manter contexto entre chamadas). "
            "Se omitido, um novo é gerado a cada execução."
        ),
    )

    args = parser.parse_args()

    if not API_URL:
        raise SystemExit(
            "AGENT_API_URL não definido. Configure no .env (ex.: "
            "AGENT_API_URL=http://192.168.2.20:5678/webhook/seu-endpoint)."
        )

    arquivos = montar_lista_arquivos(args.tipo, args)
    pergunta = args.pergunta or PERGUNTAS_PADRAO[args.tipo]
    session_id = args.session_id or str(uuid.uuid4())

    retorno = ask_to_agent(
        pergunta, tipo=args.tipo, session_id=session_id, file_paths=arquivos
    )

    print(f"\nResposta:\n{retorno}")


if __name__ == "__main__":
    main()