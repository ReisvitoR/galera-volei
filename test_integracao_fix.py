"""
Testes de integração para o sistema de convites
Testa o fluxo completo da API via HTTP
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys
import os

# Configurações
API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

class TestIntegracao:
    """Classe para testes de integração da API"""
    
    def __init__(self):
        self.tokens = {}
        self.usuarios = {}
        self.partidas = {}
        self.convites = {}
        self.resultados = []
    
    def log_resultado(self, teste, sucesso, mensagem=""):
        """Registrar resultado de um teste"""
        status = "PASSOU" if sucesso else "FALHOU"
        self.resultados.append({
            "teste": teste,
            "sucesso": sucesso,
            "mensagem": mensagem,
            "timestamp": datetime.now()
        })
        print(f"{status}: {teste}")
        if mensagem:
            print(f"  -> {mensagem}")
    
    def fazer_requisicao(self, method, endpoint, headers=None, data=None):
        """Fazer requisição HTTP e retornar status e resposta"""
        url = f"{API_V1}{endpoint}"
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=5)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=5)
            elif method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=5)
            else:
                return None, None
            
            return response.status_code, response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            return None, {"error": str(e)}
    
    def obter_token_valido(self):
        """Obter token de autenticação válido"""
        # Tentar registrar usuário de teste
        user_data = {
            "nome": "Teste Integração",
            "email": f"teste_integracao_{int(time.time())}@test.com",
            "senha": "senha123"
        }
        
        status, response = self.fazer_requisicao("POST", "/auth/register", data=user_data)
        if status != 201:
            return None
        
        # O registro já retorna o token
        return response.get("access_token")
    
    def criar_partida_teste(self, token, publica=False):
        """Criar uma partida para testes"""
        headers = {"Authorization": f"Bearer {token}"}
        partida_data = {
            "titulo": f"Partida Teste {int(time.time())}",
            "descricao": "Partida para testes de integração",
            "tipo": "normal",  # Usar string em vez de enum
            "data_partida": (datetime.now() + timedelta(days=1)).isoformat(),
            "local": "Quadra Teste",
            "max_participantes": 12,
            "publica": publica
        }
        
        status, response = self.fazer_requisicao("POST", "/partidas/", headers=headers, data=partida_data)
        print(f"DEBUG: Criar partida - Status: {status}, Response: {response}")
        return response.get("id") if status == 201 else None
    
    def criar_usuario_teste(self, sufixo=""):
        """Criar usuário de teste"""
        user_data = {
            "nome": f"Usuario Teste {sufixo}",
            "email": f"usuario_teste_{sufixo}_{int(time.time())}@test.com",
            "senha": "senha123"
        }
        
        status, response = self.fazer_requisicao("POST", "/auth/register", data=user_data)
        if status == 201:
            return {
                "id": response.get("user", {}).get("id"),  # Acessa user.id na resposta
                "token": response.get("access_token"),
                "email": user_data["email"]
            }
        
        return None
    
    def teste_fluxo_completo_convites(self):
        """Teste do fluxo completo de convites"""
        print("\n" + "="*50)
        print("TESTE: Fluxo Completo de Convites")
        print("="*50)
        
        # Criar usuários
        mandante = self.criar_usuario_teste("mandante")
        if not mandante:
            self.log_resultado("Criar usuário mandante", False, "Falha ao criar usuário mandante")
            return
        
        convidado = self.criar_usuario_teste("convidado")
        if not convidado:
            self.log_resultado("Criar usuário convidado", False, "Falha ao criar usuário convidado")
            return
        
        self.log_resultado("Criar usuários", True, "Usuários criados com sucesso")
        
        # Criar partida privada
        headers_mandante = {"Authorization": f"Bearer {mandante['token']}"}
        partida_id = self.criar_partida_teste(mandante['token'], publica=False)
        
        if not partida_id:
            self.log_resultado("Criar partida privada", False, "Falha ao criar partida")
            return
        
        self.log_resultado("Criar partida privada", True, f"Partida criada com ID {partida_id}")
        
        # Enviar convite
        convite_data = {
            "convidado_id": convidado["id"],
            "partida_id": partida_id,
            "mensagem": "Venha jogar conosco!"
        }
        
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers_mandante, data=convite_data)
        
        if status == 201:
            convite_id = response["id"]
            self.log_resultado("Enviar convite", True, f"Convite enviado com ID {convite_id}")
        else:
            self.log_resultado("Enviar convite", False, f"Status: {status}, Response: {response}")
            return
        
        # Listar convites do convidado
        headers_convidado = {"Authorization": f"Bearer {convidado['token']}"}
        status, response = self.fazer_requisicao("GET", "/convites/recebidos", headers=headers_convidado)
        
        if status == 200 and len(response) > 0:
            self.log_resultado("Listar convites recebidos", True, f"Encontrados {len(response)} convites")
        else:
            self.log_resultado("Listar convites recebidos", False, f"Status: {status}")
        
        # Aceitar convite
        status, response = self.fazer_requisicao("PUT", f"/convites/{convite_id}/aceitar", headers=headers_convidado)
        
        if status == 200:
            self.log_resultado("Aceitar convite", True, "Convite aceito com sucesso")
        else:
            self.log_resultado("Aceitar convite", False, f"Status: {status}, Response: {response}")
    
    def teste_validacoes_basicas(self):
        """Teste validações básicas da API"""
        print("\n" + "="*50)
        print("TESTE: Validações Básicas")
        print("="*50)
        
        token = self.obter_token_valido()
        if not token:
            self.log_resultado("Obter token", False, "Falha ao obter token")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tentar enviar convite sem dados
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data={})
        
        if status == 422:  # Validation Error
            self.log_resultado("Validação dados vazios", True, "API rejeitou dados vazios corretamente")
        else:
            self.log_resultado("Validação dados vazios", False, f"Status esperado 422, recebido {status}")
        
        # Tentar acessar convite inexistente
        status, response = self.fazer_requisicao("GET", "/convites/99999", headers=headers)
        
        if status == 404:
            self.log_resultado("Convite inexistente", True, "API retornou 404 para convite inexistente")
        else:
            self.log_resultado("Convite inexistente", False, f"Status esperado 404, recebido {status}")
    
    def teste_autenticacao(self):
        """Teste sistema de autenticação"""
        print("\n" + "="*50)
        print("TESTE: Sistema de Autenticação")
        print("="*50)
        
        # Tentar acessar endpoint protegido sem token
        status, response = self.fazer_requisicao("GET", "/convites/enviados")
        
        if status == 401:
            self.log_resultado("Acesso sem token", True, "API bloqueou acesso sem autenticação")
        else:
            self.log_resultado("Acesso sem token", False, f"Status esperado 401, recebido {status}")
        
        # Tentar com token inválido
        headers = {"Authorization": "Bearer token_invalido"}
        status, response = self.fazer_requisicao("GET", "/convites/enviados", headers=headers)
        
        if status == 401:
            self.log_resultado("Token inválido", True, "API rejeitou token inválido")
        else:
            self.log_resultado("Token inválido", False, f"Status esperado 401, recebido {status}")
    
    def executar_todos_testes(self):
        """Executar todos os testes de integração"""
        print("Iniciando testes de integração...")
        print("Certificando que o servidor está rodando...")
        
        # Verificar se servidor está online
        try:
            response = requests.get(f"{API_BASE}/", timeout=5)
            if response.status_code != 200:
                print("ERRO: Servidor não está respondendo corretamente")
                return 0, 1
        except requests.exceptions.RequestException:
            print("ERRO: Não foi possível conectar ao servidor")
            return 0, 1
        
        # Executar testes
        self.teste_autenticacao()
        self.teste_validacoes_basicas()
        self.teste_fluxo_completo_convites()
        
        # Calcular resultados
        sucessos = sum(1 for r in self.resultados if r["sucesso"])
        falhas = len(self.resultados) - sucessos
        total = len(self.resultados)
        
        print(f"\n" + "="*60)
        print("RELATÓRIO DE TESTES DE INTEGRAÇÃO")
        print("="*60)
        
        for resultado in self.resultados:
            status = "PASSOU" if resultado["sucesso"] else "FALHOU"
            print(f"{status}: {resultado['teste']}")
            if resultado["mensagem"]:
                print(f"  -> {resultado['mensagem']}")
        
        print(f"\n{'='*60}")
        print(f"Total de testes: {total}")
        print(f"Sucessos: {sucessos}")
        print(f"Falhas: {falhas}")
        
        if total > 0:
            taxa_sucesso = (sucessos / total) * 100
            print(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
            
            if taxa_sucesso >= 90:
                print("EXCELENTE! Sistema funcionando perfeitamente!")
            elif taxa_sucesso >= 75:
                print("BOM! Sistema funcionando bem com alguns ajustes necessários")
            elif taxa_sucesso >= 50:
                print("REGULAR! Sistema parcialmente funcional")
            else:
                print("CRÍTICO! Sistema com problemas sérios")
        
        return sucessos, falhas


def main():
    """Função principal para executar testes de integração"""
    testador = TestIntegracao()
    sucessos, falhas = testador.executar_todos_testes()
    
    # Retornar código de saída apropriado
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)