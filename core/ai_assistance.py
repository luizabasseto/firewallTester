# core/ai_assistant.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

class AIAssistant:
    """
    Classe de backend para lidar com as chamadas à API de IA Generativa.
    """
    def __init__(self):
        """
        Configura a API ao inicializar a classe.
        """
        load_dotenv()
        try:
            # Carrega a chave da API da variável de ambiente (forma segura)
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
            self.is_configured = True
        except Exception as e:
            print(f"Erro ao configurar o Assistente de IA: {e}")
            self.is_configured = False

    def explain_firewall_rule(self, rule_string):
        """
        Envia uma regra de firewall para a IA e pede uma explicação.

        Args:
            rule_string (str): A regra de iptables a ser explicada.

        Returns:
            str: A explicação formatada ou uma mensagem de erro.
        """
        if not self.is_configured:
            return "O Assistente de IA não está configurado corretamente."

        prompt = f"""
        Você é um especialista em segurança de redes e firewalls Linux, com foco em `iptables`.
        Sua tarefa é explicar a seguinte regra de firewall de forma clara e concisa para um estudante de redes.
        Se a entrada não for uma regra válida, informe de forma educada.

        Divida a explicação nos seguintes tópicos:
        - **Objetivo:** Qual o propósito principal da regra?
        - **Componentes:** Detalhe o que cada parte da regra significa (ex: -A, -p, -j).
        - **Efeito Prático:** O que acontece com os pacotes de rede que correspondem a esta regra?

        Regra para analisar:
        ```
        {rule_string}
        ```
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Ocorreu um erro ao comunicar com a IA: {e}"