import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("AGENT_API_URL")

def ask_to_agent(ask):
    
    payload = {
        "chatInput": ask,
        "sessionId": "sessao-luiza-001"
    }

    print(f"Trying to talk with the servidor...")

    try:
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
    retorno = ""
    if(pergunta):
        retorno = ask_to_agent(pergunta)
        
    print(f"\n Answer: \n{retorno}" )
