"""
Script de testes automatizados usando requests
Executa testes reais contra a API do sistema de convites
"""

import requests
import json
from datetime import datetime, timedelta
import time

class CorAnsi:
    """Cores ANSI para output colorido"""
    VERDE = '\033[92m'
    VERMELHO = '\033[91m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIANO = '\033[96m'
    BRANCO = '\033[97m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'

class TestadorAPI:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.tokens = {}
        self.usuarios = {}
        self.partidas = {}
        self.convites = {}
        self.resultados = {
            'passou': 0,
            'falhou': 0,
            'total': 0
        }
    
    def log(self, mensagem, cor=CorAnsi.BRANCO):
        print(f"{cor}{mensagem}{CorAnsi.RESET}")
    
    def sucesso(self, mensagem):
        self.log(f"✅ {mensagem}", CorAnsi.VERDE)
        self.resultados['passou'] += 1
    
    def falha(self, mensagem):
        self.log(f"❌ {mensagem}", CorAnsi.VERMELHO)
        self.resultados['falhou'] += 1
    
    def info(self, mensagem):
        self.log(f"ℹ️  {mensagem}", CorAnsi.AZUL)
    
    def aviso(self, mensagem):
        self.log(f"⚠️  {mensagem}", CorAnsi.AMARELO)
    
    def titulo(self, mensagem):
        self.log(f"\n{CorAnsi.NEGRITO}{'='*60}", CorAnsi.CIANO)
        self.log(f"{mensagem}", CorAnsi.CIANO)
        self.log(f"{'='*60}{CorAnsi.RESET}", CorAnsi.CIANO)
    
    def executar_teste(self, nome, func_teste):
        """Executa um teste e registra o resultado"""
        self.resultados['total'] += 1
        self.log(f"\n🧪 {nome}", CorAnsi.MAGENTA)
        
        try:
            resultado = func_teste()
            if resultado:
                self.sucesso(f"{nome} - OK")
                return True
            else:
                self.falha(f"{nome} - FALHOU")
                return False
        except Exception as e:
            self.falha(f"{nome} - ERRO: {str(e)}")
            return False
    
    def fazer_requisicao(self, method, endpoint, headers=None, data=None, esperado_status=None):
        """Faz uma requisição HTTP e valida a resposta"""
        url = f"{self.api_url}{endpoint}" if endpoint.startswith('/') else f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=headers, json=data, timeout=10)
            
            self.info(f"{method} {url} -> {response.status_code}")
            
            if esperado_status and response.status_code != esperado_status:
                self.aviso(f"Status esperado: {esperado_status}, recebido: {response.status_code}")
            
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text
                
        except requests.exceptions.ConnectionError:
            self.falha("Não foi possível conectar ao servidor")
            return None, None
        except Exception as e:
            self.falha(f"Erro na requisição: {str(e)}")
            return None, None
    
    # FASE 1: TESTES DE INFRAESTRUTURA
    def teste_health_check(self):
        status, data = self.fazer_requisicao("GET", "/health", esperado_status=200)
        return status == 200 and isinstance(data, dict) and data.get('status') == 'ok'
    
    def teste_documentacao(self):
        status, data = self.fazer_requisicao("GET", "/docs", esperado_status=200)
        return status == 200
    
    # FASE 2: TESTES DE AUTENTICAÇÃO
    def teste_registro_usuario1(self):
        data = {
            "nome": "João Organizador",
            "email": "joao@test.com",
            "senha": "123456"
        }
        status, response = self.fazer_requisicao("POST", "/auth/register", data=data)
        
        if status == 201:
            self.usuarios['user1'] = response
            return True
        elif status == 400 and "already registered" in str(response):
            self.aviso("Usuário já existe - OK para testes")
            return True
        return False
    
    def teste_registro_usuario2(self):
        data = {
            "nome": "Maria Convidada",
            "email": "maria@test.com", 
            "senha": "123456"
        }
        status, response = self.fazer_requisicao("POST", "/auth/register", data=data)
        
        if status == 201:
            self.usuarios['user2'] = response
            return True
        elif status == 400 and "already registered" in str(response):
            self.aviso("Usuário já existe - OK para testes")
            return True
        return False
    
    def teste_registro_usuario3(self):
        data = {
            "nome": "Pedro Terceiro",
            "email": "pedro@test.com",
            "senha": "123456"
        }
        status, response = self.fazer_requisicao("POST", "/auth/register", data=data)
        
        if status == 201:
            self.usuarios['user3'] = response
            return True
        elif status == 400 and "already registered" in str(response):
            self.aviso("Usuário já existe - OK para testes")
            return True
        return False
    
    def teste_login_usuario1(self):
        # Usar form data para login
        import requests
        data = {
            "username": "joao@test.com",
            "password": "123456"
        }
        url = f"{self.api_url}/auth/login"
        
        try:
            response = requests.post(url, data=data, timeout=10)
            self.info(f"POST {url} -> {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                self.tokens['user1'] = json_data.get('access_token')
                return True
        except Exception as e:
            self.falha(f"Erro no login: {str(e)}")
        return False
    
    def teste_login_usuario2(self):
        import requests
        data = {
            "username": "maria@test.com",
            "password": "123456"
        }
        url = f"{self.api_url}/auth/login"
        
        try:
            response = requests.post(url, data=data, timeout=10)
            self.info(f"POST {url} -> {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                self.tokens['user2'] = json_data.get('access_token')
                return True
        except Exception as e:
            self.falha(f"Erro no login: {str(e)}")
        return False
    
    def teste_login_usuario3(self):
        import requests
        data = {
            "username": "pedro@test.com",
            "password": "123456"
        }
        url = f"{self.api_url}/auth/login"
        
        try:
            response = requests.post(url, data=data, timeout=10)
            self.info(f"POST {url} -> {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                self.tokens['user3'] = json_data.get('access_token')
                return True
        except Exception as e:
            self.falha(f"Erro no login: {str(e)}")
        return False
    
    # FASE 3: TESTES DE PARTIDAS
    def teste_criar_partida_publica(self):
        if not self.tokens.get('user1'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user1']}"}
        data = {
            "titulo": "Partida Pública - Teste",
            "descricao": "Partida aberta para todos",
            "data_hora": (datetime.now() + timedelta(days=1)).isoformat(),
            "local": "Quadra Central",
            "max_participantes": 12,
            "publica": True
        }
        
        status, response = self.fazer_requisicao("POST", "/partidas/", headers=headers, data=data)
        
        if status == 201:
            self.partidas['publica'] = response
            return True
        return False
    
    def teste_criar_partida_privada(self):
        if not self.tokens.get('user1'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user1']}"}
        data = {
            "titulo": "Partida Privada - Teste",
            "descricao": "Partida apenas por convite",
            "data_hora": (datetime.now() + timedelta(days=2)).isoformat(),
            "local": "Quadra VIP",
            "max_participantes": 8,
            "publica": False
        }
        
        status, response = self.fazer_requisicao("POST", "/partidas/", headers=headers, data=data)
        
        if status == 201:
            self.partidas['privada'] = response
            return True
        return False
    
    def teste_listar_partidas(self):
        status, response = self.fazer_requisicao("GET", "/partidas/")
        return status == 200 and isinstance(response, list)
    
    # FASE 4: TESTES DE CONVITES - CENÁRIOS POSITIVOS
    def teste_enviar_convite_valido(self):
        if not all([self.tokens.get('user1'), self.partidas.get('privada')]):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user1']}"}
        data = {
            "mensagem": "Olá! Você está convidado para nossa partida de vôlei!",
            "data_expiracao": (datetime.now() + timedelta(days=7)).isoformat(),
            "convidado_id": 2,  # Assumindo ID do user2
            "partida_id": self.partidas['privada']['id']
        }
        
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=data)
        
        if status == 201:
            self.convites['convite1'] = response
            return True
        return False
    
    def teste_listar_convites_enviados(self):
        if not self.tokens.get('user1'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user1']}"}
        status, response = self.fazer_requisicao("GET", "/convites/enviados", headers=headers)
        return status == 200 and isinstance(response, list)
    
    def teste_listar_convites_recebidos(self):
        if not self.tokens.get('user2'):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user2']}"}
        status, response = self.fazer_requisicao("GET", "/convites/recebidos", headers=headers)
        return status == 200 and isinstance(response, list)
    
    def teste_aceitar_convite(self):
        if not all([self.tokens.get('user2'), self.convites.get('convite1')]):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user2']}"}
        convite_id = self.convites['convite1']['id']
        
        status, response = self.fazer_requisicao("PUT", f"/convites/{convite_id}/aceitar", headers=headers)
        return status == 200
    
    # FASE 5: TESTES DE CENÁRIOS NEGATIVOS
    def teste_convite_partida_publica(self):
        """Deve falhar - não pode enviar convite para partida pública"""
        if not all([self.tokens.get('user1'), self.partidas.get('publica')]):
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['user1']}"}
        data = {
            "mensagem": "Convite inválido para partida pública",
            "convidado_id": 3,
            "partida_id": self.partidas['publica']['id']
        }
        
        status, response = self.fazer_requisicao("POST", "/convites/", headers=headers, data=data)
        return status == 400  # Deve falhar
    
    def teste_convite_sem_autorizacao(self):
        """Deve falhar - acesso sem token"""
        status, response = self.fazer_requisicao("GET", "/convites/enviados")
        return status == 401  # Deve falhar
    
    def executar_todos_os_testes(self):
        """Executa toda a bateria de testes"""
        self.titulo("🚀 INICIANDO BATERIA COMPLETA DE TESTES AUTOMATIZADOS")
        
        # FASE 1: INFRAESTRUTURA
        self.titulo("FASE 1: TESTES DE INFRAESTRUTURA")
        self.executar_teste("Health Check da API", self.teste_health_check)
        self.executar_teste("Acessibilidade da documentação", self.teste_documentacao)
        
        # FASE 2: AUTENTICAÇÃO
        self.titulo("FASE 2: TESTES DE AUTENTICAÇÃO")
        self.executar_teste("Registrar usuário 1 (Organizador)", self.teste_registro_usuario1)
        self.executar_teste("Registrar usuário 2 (Convidado)", self.teste_registro_usuario2)
        self.executar_teste("Registrar usuário 3 (Extra)", self.teste_registro_usuario3)
        self.executar_teste("Login usuário 1", self.teste_login_usuario1)
        self.executar_teste("Login usuário 2", self.teste_login_usuario2)
        self.executar_teste("Login usuário 3", self.teste_login_usuario3)
        
        # FASE 3: PARTIDAS
        self.titulo("FASE 3: TESTES DE PARTIDAS")
        self.executar_teste("Criar partida pública", self.teste_criar_partida_publica)
        self.executar_teste("Criar partida privada", self.teste_criar_partida_privada)
        self.executar_teste("Listar todas as partidas", self.teste_listar_partidas)
        
        # FASE 4: CONVITES POSITIVOS
        self.titulo("FASE 4: TESTES DO SISTEMA DE CONVITES")
        self.executar_teste("Enviar convite válido", self.teste_enviar_convite_valido)
        self.executar_teste("Listar convites enviados", self.teste_listar_convites_enviados)
        self.executar_teste("Listar convites recebidos", self.teste_listar_convites_recebidos)
        self.executar_teste("Aceitar convite", self.teste_aceitar_convite)
        
        # FASE 5: CENÁRIOS NEGATIVOS
        self.titulo("FASE 5: TESTES DE CENÁRIOS NEGATIVOS")
        self.executar_teste("Convite para partida pública (deve falhar)", self.teste_convite_partida_publica)
        self.executar_teste("Acesso sem autorização (deve falhar)", self.teste_convite_sem_autorizacao)
        
        # RESULTADOS FINAIS
        self.titulo("📊 RESULTADOS FINAIS")
        self.log(f"Total de testes: {self.resultados['total']}", CorAnsi.BRANCO)
        self.log(f"Sucessos: {self.resultados['passou']}", CorAnsi.VERDE)
        self.log(f"Falhas: {self.resultados['falhou']}", CorAnsi.VERMELHO)
        
        taxa_sucesso = (self.resultados['passou'] / self.resultados['total']) * 100 if self.resultados['total'] > 0 else 0
        self.log(f"Taxa de sucesso: {taxa_sucesso:.1f}%", CorAnsi.CIANO)
        
        if taxa_sucesso >= 80:
            self.sucesso("🎉 SISTEMA FUNCIONANDO CORRETAMENTE!")
        elif taxa_sucesso >= 60:
            self.aviso("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        else:
            self.falha("❌ SISTEMA COM PROBLEMAS CRÍTICOS")

def main():
    """Função principal"""
    testador = TestadorAPI()
    testador.executar_todos_os_testes()

if __name__ == "__main__":
    main()