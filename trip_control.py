import requests
import json
import streamlit as st
from typing import Union, List, Dict

class TripControl:
    def __init__(self, token: str, gist_id: str):
        if not token:
            raise ValueError("❌ ERRO: O token do GitHub não foi fornecido.")
        
        self.token = token
        self.gist_id = gist_id
        # O nome do arquivo no Gist é um detalhe de implementação interno e fixo.
        self.filename = "dados_viagem.json" 
        self.api_headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }
        
        # A autenticação é chamada no momento da criação do objeto.
        self._autenticar()

    def _autenticar(self):
        """Método privado para verificar o token na inicialização."""
        print("--- Verificando autenticação com o GitHub... ---")
        url = "https://api.github.com/user"
        try:
            response = requests.get(url, headers=self.api_headers)
            response.raise_for_status() # Lança erro para status 4xx ou 5xx
            usuario = response.json()
            print(f"✅ Autenticação bem-sucedida como '{usuario['login']}'.")
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise ConnectionError("ERRO DE AUTENTICAÇÃO: O token fornecido é inválido ou expirou.")
            else:
                raise ConnectionError(f"Falha na autenticação com status: {err.response.status_code}.")
        except requests.exceptions.RequestException as err:
            raise ConnectionError(f"Erro de conexão com a API do GitHub: {err}")

    def consultar_dados(self) -> Union[List[Dict], None]:
        """Consulta o Gist e retorna todo o conteúdo do arquivo JSON."""
        print(f"\n--- Consultando dados do Gist '{self.gist_id}'... ---")
        url = f"https://api.github.com/gists/{self.gist_id}"
        try:
            response = requests.get(url, headers=self.api_headers)
            response.raise_for_status()
            gist_data = response.json()
            conteudo_string = gist_data["files"][self.filename]["content"]
            print("✅ Dados lidos com sucesso!")
            return json.loads(conteudo_string)
        except Exception as err:
            print(f"❌ Erro ao consultar o Gist: {err}")
            return None

    def atualizar_dados(self, novo_conteudo: List[Dict]) -> bool:
        """Sobrescreve o arquivo no Gist com o novo conteúdo."""
        print(f"--- Atualizando dados no Gist... ---")
        url = f"https://api.github.com/gists/{self.gist_id}"
        payload = {"files": {self.filename: {"content": json.dumps(novo_conteudo, indent=2)}}}
        try:
            response = requests.patch(url, headers=self.api_headers, json=payload)
            response.raise_for_status()
            print("✅ Gist atualizado com sucesso no GitHub!")
            return True
        except Exception as err:
            print(f"❌ Erro ao atualizar o Gist: {err}")
            return False

def toggle_menu():
    st.session_state.menu_visivel = not st.session_state.menu_visivel
