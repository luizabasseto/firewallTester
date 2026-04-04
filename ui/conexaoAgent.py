import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("AGENT_API_URL")

def ask_to_agent(ask, file_path=None):
    
    payload = {
        "chatInput": ask,
        "sessionId": "sessao-luiza-001"
    }

    print(f"Trying to talk with the servidor...")

    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                files = {'arquivo_enviado': (os.path.basename(file_path), f)}
                
                response = requests.post(API_URL, data=payload, files=files, timeout=60)
        else:
            response = requests.post(API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            dados = response.json()
            
            if isinstance(dados, list):
                dados = dados[0]
            
            resposta_final = dados.get('output', 'A IA processou, mas o campo "output" não foi encontrado.')
            
            return resposta_final
            
        elif response.status_code == 404:
            return "Erro 404: Webhook não encontrado. Verifique se o Workflow está ATIVO (Published) no n8n."
        else:
            return f"Erro no servidor ({response.status_code}): {response.text}"

    except requests.exceptions.ConnectionError:
        return "Falha técnica: Não foi possível conectar ao servidor. O túnel do VS Code (porta 5678) está ativo?"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"


if __name__ == "__main__":
    pergunta = input("What is your doubt? \n")
    
    caminho_arquivo = input("Digite o caminho do arquivo (PDF, JSON, etc) ou aperte ENTER para enviar sem arquivo: \n").strip()
    
    retorno = ""
    if pergunta:
        if caminho_arquivo:
            retorno = ask_to_agent(pergunta, file_path=caminho_arquivo)
        else:
            retorno = ask_to_agent(pergunta)
            
    print(f"\n Answer: \n{retorno}")