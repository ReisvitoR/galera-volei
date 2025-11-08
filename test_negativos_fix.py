"""
Testes de cenários negativos para validar robustez do sistema
Testa casos extremos, inputs inválidos e condições de erro
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configurações
API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

class TestCenariosNegativos:
    """Classe para testes de cenários negativos"""
    
    def __init__(self):
        self.resultados = []
    
    def log_resultado(self, teste, sucesso, mensagem=""):
        """Registrar resultado de um teste"""
        status_emoji = "PASSOU" if sucesso else "FALHOU"
        self.resultados.append({
            "teste": teste,
            "sucesso": sucesso,
            "mensagem": mensagem,
            "timestamp": datetime.now()
        })
        print(f"{status_emoji}: {teste}")
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
        user_data = {
            "nome": "Teste Negativo",
            "email": f"teste_negativo_{int(time.time())}@test.com",
            "senha": "senha123"
        }
        
        status, response = self.fazer_requisicao("POST", "/auth/register", data=user_data)
        if status == 201 and "access_token" in response:
            return response["access_token"]
        
        return None
    
    def teste_inputs_maliciosos(self):
        """Teste com inputs maliciosos e ataques comuns"""
        print("\n" + "="*40)
        print("TESTE: Inputs Maliciosos")
        print("-" * 40)
        
        token = self.obter_token_valido()
        if not token:
            print("Não foi possível obter token para testes")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # SQL Injection
        sql_injection_data = {
            "convidado_id": "1; DROP TABLE convites; --",
            "partida_id": 1,
            "mensagem": "'; DELETE FROM users; --"
        }
        
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=sql_injection_data)
        
        if status == 422:  # Validation error esperado
            self.log_resultado("SQL Injection", True, "API rejeitou tentativa de SQL injection")
        else:
            self.log_resultado("SQL Injection", False, f"Status: {status} - API pode ser vulnerável")
        
        # XSS Script
        xss_data = {
            "convidado_id": 1,
            "partida_id": 1,
            "mensagem": "<script>alert('XSS')</script>"
        }
        
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=xss_data)
        
        if status in [422, 400]:
            self.log_resultado("XSS Script", True, "API tratou script malicioso adequadamente")
        else:
            self.log_resultado("XSS Script", False, f"Status: {status} - Possível vulnerabilidade XSS")
        
        # Payload muito grande
        payload_grande = {
            "convidado_id": 1,
            "partida_id": 1,
            "mensagem": "A" * 10000  # 10KB de dados
        }
        
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=payload_grande)
        
        if status in [413, 422]:  # Payload too large ou validation error
            self.log_resultado("Payload Grande", True, "API limitou tamanho do payload")
        else:
            self.log_resultado("Payload Grande", False, f"Status: {status} - API aceitou payload muito grande")
    
    def teste_dados_invalidos(self):
        """Teste com tipos de dados inválidos"""
        print("\n" + "="*40)
        print("TESTE: Dados Inválidos")
        print("-" * 40)
        
        token = self.obter_token_valido()
        if not token:
            print("Não foi possível obter token para testes")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tipos incorretos
        dados_incorretos = [
            {"convidado_id": "string", "partida_id": 1},  # String onde deveria ser int
            {"convidado_id": 1.5, "partida_id": 1},      # Float onde deveria ser int
            {"convidado_id": [], "partida_id": 1},        # Array onde deveria ser int
            {"convidado_id": {}, "partida_id": 1},        # Object onde deveria ser int
            {"convidado_id": None, "partida_id": 1},      # Null onde deveria ser int
        ]
        
        sucessos_validacao = 0
        for i, dados in enumerate(dados_incorretos):
            status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=dados)
            
            if status == 422:  # Validation error esperado
                sucessos_validacao += 1
            else:
                print(f"ERRO Dados inválidos {i+1} não rejeitados com status {status}")
        
        if sucessos_validacao == len(dados_incorretos):
            self.log_resultado("Validação Tipos", True, "Todos os tipos inválidos foram rejeitados")
        else:
            self.log_resultado("Validação Tipos", False, f"Apenas {sucessos_validacao}/{len(dados_incorretos)} validações passaram")
    
    def teste_ids_inexistentes(self):
        """Teste com IDs que não existem no banco"""
        print("\n" + "="*40)
        print("TESTE: IDs Inexistentes")
        print("-" * 40)
        
        token = self.obter_token_valido()
        if not token:
            print("Não foi possível obter token para testes")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # IDs muito grandes (provavelmente inexistentes)
        ids_inexistentes = [999999, 888888, 777777]
        
        for user_id in ids_inexistentes:
            dados = {
                "convidado_id": user_id,
                "partida_id": 999999,
                "mensagem": "Teste"
            }
            
            status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=dados)
            
            if status in [404, 400]:  # Not found ou bad request esperado
                self.log_resultado(f"ID Inexistente {user_id}", True, "API rejeitou ID inexistente")
            else:
                self.log_resultado(f"ID Inexistente {user_id}", False, f"Status: {status} - API não validou existência")
    
    def teste_limite_requisicoes(self):
        """Teste de limite de requisições (rate limiting)"""
        print("\n" + "="*40)
        print("TESTE: Limite de Requisições")
        print("-" * 40)
        
        token = self.obter_token_valido()
        if not token:
            print("Não foi possível obter token para testes")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Fazer muitas requisições rapidamente
        requisicoes_bloqueadas = 0
        total_requisicoes = 20
        
        for i in range(total_requisicoes):
            status, response = self.fazer_requisicao("GET", "/convites/enviados", headers=headers)
            
            if status == 429:  # Too Many Requests
                requisicoes_bloqueadas += 1
            elif status is None:
                print(f"ERRO Requisição {i+1} falhou com status {status}")
        
        if requisicoes_bloqueadas > 0:
            self.log_resultado("Rate Limiting", True, f"{requisicoes_bloqueadas} requisições bloqueadas por rate limiting")
        else:
            self.log_resultado("Rate Limiting", False, "Nenhuma proteção contra spam de requisições detectada")
    
    def teste_autenticacao_quebrada(self):
        """Teste tentativas de quebrar autenticação"""
        print("\n" + "="*40)
        print("TESTE: Quebra de Autenticação")
        print("-" * 40)
        
        # Tokens malformados
        tokens_invalidos = [
            "",
            "Bearer ",
            "Bearer token_inexistente",
            "Bearer " + "a" * 500,  # Token muito longo
            "Invalid_Format",
            "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",  # JWT malformado
        ]
        
        sucessos_seguranca = 0
        for token_invalido in tokens_invalidos:
            headers = {"Authorization": token_invalido}
            status, response = self.fazer_requisicao("GET", "/convites/enviados", headers=headers)
            
            if status == 401:  # Unauthorized esperado
                sucessos_seguranca += 1
        
        if sucessos_seguranca == len(tokens_invalidos):
            self.log_resultado("Tokens Malformados", True, "Todos os tokens inválidos foram rejeitados")
        else:
            self.log_resultado("Tokens Malformados", False, f"Apenas {sucessos_seguranca}/{len(tokens_invalidos)} tokens foram rejeitados")
        
        # Tentar acessar recursos de outros usuários
        token = self.obter_token_valido()
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Tentar acessar convite de outro usuário (ID muito alto)
            status, response = self.fazer_requisicao("GET", "/convites/999999", headers=headers)
            
            if status in [404, 403]:  # Not found ou forbidden
                self.log_resultado("Acesso Não Autorizado", True, "API bloqueou acesso a recurso de outro usuário")
            else:
                self.log_resultado("Acesso Não Autorizado", False, f"Status: {status} - Possível vazamento de dados")
    
    def executar_todos_testes(self):
        """Executar todos os testes de cenários negativos"""
        print("Iniciando testes de cenários negativos...")
        print("Certifique-se de que o servidor está rodando em http://127.0.0.1:8000")
        
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
        self.teste_inputs_maliciosos()
        self.teste_dados_invalidos()
        self.teste_ids_inexistentes()
        self.teste_limite_requisicoes()
        self.teste_autenticacao_quebrada()
        
        # Calcular resultados
        sucessos = sum(1 for r in self.resultados if r["sucesso"])
        falhas = len(self.resultados) - sucessos
        total = len(self.resultados)
        
        print(f"\n" + "="*60)
        print("RELATÓRIO DE TESTES DE CENÁRIOS NEGATIVOS")
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
            
            if taxa_sucesso >= 80:
                print("OK! Maioria dos casos negativos tratados")
            elif taxa_sucesso >= 60:
                print("REGULAR! Alguns casos negativos precisam ser tratados")
            else:
                print("ATENÇÃO! Muitos casos negativos não tratados adequadamente")
        
        return sucessos, falhas


def main():
    """Função principal para executar testes negativos"""
    testador = TestCenariosNegativos()
    sucessos, falhas = testador.executar_todos_testes()
    
    # Retornar código de saída apropriado
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)