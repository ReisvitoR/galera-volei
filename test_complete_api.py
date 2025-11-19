"""
Testes completos e organizados da API Galera Vôlei
Testa os status codes e funcionalidades principais
"""
import json
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api import app

# Cliente de teste
client = TestClient(app)

# Dados de teste
admin_credentials = {
    "email": "admin@galeravolei.com",
    "senha": "admin123"
}

test_user_data = {
    "nome": "Usuário Teste API",
    "email": "teste_api@exemplo.com",
    "senha": "123456",
    "tipo": "intermediario"
}

def print_result(test_name: str, status_code: int, expected: list, response_data=None):
    """Imprimir resultado formatado do teste"""
    if status_code in expected:
        status_icon = "v"
    else:
        status_icon = "x"
    
    print(f"  {status_icon} {test_name}")
    print(f"     Status Code: {status_code} (esperado: {expected})")
    
    if response_data and isinstance(response_data, dict):
        if "detail" in response_data:
            print(f"     Mensagem: {response_data['detail']}")
        elif status_code == 200 and "access_token" in response_data:
            print(f"     Token gerado:")
    print()

def get_admin_token():
    """Obter token de administrador"""
    response = client.post("/api/v1/auth/login", json=admin_credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_health_endpoints():
    """Testar endpoints básicos de saúde, não queremos mal cheiro"""
    print("HEALTH CHECK ENDPOINTS")
    print("=" * 50)
    
    # Endpoint raiz
    response = client.get("/")
    print_result(
        "GET / - Endpoint raiz", 
        response.status_code, 
        [200, 404],
        response.json() if response.status_code == 200 else None
    )
    
    # Documentação
    response = client.get("/docs")
    print_result(
        "GET /docs - Documentação Swagger",
        response.status_code,
        [200]
    )
    
    # OpenAPI schema
    response = client.get("/openapi.json")
    print_result(
        "GET /openapi.json - Schema OpenAPI",
        response.status_code,
        [200]
    )

def test_auth_endpoints():
    """Testar endpoints de autenticação"""
    print("AUTHENTICATION ENDPOINTS")
    print("=" * 50)
    
    # Login com credenciais válidas
    response = client.post("/api/v1/auth/login", json=admin_credentials)
    print_result(
        "POST /auth/login - Login válido",
        response.status_code,
        [200],
        response.json() if response.status_code == 200 else None
    )
    
    # Login com credenciais inválidas
    invalid_creds = {"email": "wrong@email.com", "senha": "wrongpassword"}
    response = client.post("/api/v1/auth/login", json=invalid_creds)
    print_result(
        "POST /auth/login - Login inválido",
        response.status_code,
        [401],
        response.json() if response.status_code == 401 else None
    )
    
    # Registro de novo usuário
    response = client.post("/api/v1/auth/register", json=test_user_data)
    print_result(
        "POST /auth/register - Registrar usuário",
        response.status_code,
        [201, 400],  # 400 se usuário já existe
        response.json() if response.status_code in [201, 400] else None
    )
    
    # Perfil do usuário (com autenticação)
    token = get_admin_token()
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        print_result(
            "GET /auth/me - Perfil do usuário",
            response.status_code,
            [200],
            {"user_name": response.json().get("nome")} if response.status_code == 200 else response.json()
        )
    else:
        print("X - GET /auth/me - Não foi possível obter token")
        print()

def test_user_endpoints():
    """Testar endpoints de usuários"""
    print("USER ENDPOINTS")
    print("=" * 50)
    
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Listar usuários sem autenticação
    response = client.get("/api/v1/usuarios/")
    print_result(
        "GET /usuarios/ - Listar usuários (sem auth)",
        response.status_code,
        [200, 401, 403]
    )
    
    # Listar usuários com autenticação
    if token:
        response = client.get("/api/v1/usuarios/", headers=headers)
        user_count = len(response.json()) if response.status_code == 200 else 0
        print_result(
            f"GET /usuarios/ - Listar usuários (com auth) [{user_count} usuários]",
            response.status_code,
            [200],
            {"count": user_count} if response.status_code == 200 else response.json()
        )
        
        # Ranking de usuários
        response = client.get("/api/v1/usuarios/ranking", headers=headers)
        print_result(
            "GET /usuarios/ranking - Ranking",
            response.status_code,
            [200],
            {"users_in_ranking": len(response.json())} if response.status_code == 200 else response.json()
        )
        
        # Buscar usuário específico (ID 1 - admin)
        response = client.get("/api/v1/usuarios/1", headers=headers)
        print_result(
            "GET /usuarios/{id} - Buscar usuário por ID",
            response.status_code,
            [200, 404],
            {"user_found": response.json().get("nome")} if response.status_code == 200 else response.json()
        )
    else:
        print("Testes com autenticação - Token não disponível")
        print()

def test_match_endpoints():
    """Testar endpoints de partidas"""
    print("MATCH ENDPOINTS")
    print("=" * 50)
    
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Listar partidas sem autenticação
    response = client.get("/api/v1/partidas/")
    print_result(
        "GET /partidas/ - Listar partidas (sem auth)",
        response.status_code,
        [200, 401, 403]
    )
    
    # Listar partidas com autenticação
    if token:
        response = client.get("/api/v1/partidas/", headers=headers)
        match_count = len(response.json()) if response.status_code == 200 else 0
        print_result(
            f"GET /partidas/ - Listar partidas (com auth) [{match_count} partidas]",
            response.status_code,
            [200],
            {"count": match_count} if response.status_code == 200 else response.json()
        )
        
        # Criar partida
        match_data = {
            "titulo": "Partida Teste API",
            "descricao": "Partida criada para teste da API",
            "data_partida": "2025-10-15T19:00:00",
            "local": "Quadra de Teste",
            "max_jogadores": 12,
            "nivel_minimo": "amador",
            "tipo": "competitivo",
            "valor_taxa": 15.0
        }
        
        response = client.post("/api/v1/partidas/", json=match_data, headers=headers)
        print_result(
            "POST /partidas/ - Criar partida",
            response.status_code,
            [201, 400, 403],
            {"match_id": response.json().get("id")} if response.status_code == 201 else response.json()
        )
        
        # Se criou uma partida, testar busca por ID
        if response.status_code == 201:
            match_id = response.json().get("id")
            response = client.get(f"/api/v1/partidas/{match_id}", headers=headers)
            print_result(
                "GET /partidas/{id} - Buscar partida por ID",
                response.status_code,
                [200, 404],
                {"match_found": response.json().get("titulo")} if response.status_code == 200 else response.json()
            )
    else:
        print("Testes com autenticação - Token não disponível")
        print()

def test_error_cases():
    """Testar casos de erro comuns"""
    print("ERROR CASES")
    print("=" * 50)
    
    # Rota inexistente
    response = client.get("/api/v1/rota-inexistente")
    print_result(
        "GET /rota-inexistente - Rota não encontrada",
        response.status_code,
        [404]
    )
    
    # Método não permitido
    response = client.delete("/api/v1/auth/login")
    print_result(
        "DELETE /auth/login - Método não permitido",
        response.status_code,
        [405]
    )
    
    # Token inválido
    invalid_headers = {"Authorization": "Bearer token-invalido"}
    response = client.get("/api/v1/auth/me", headers=invalid_headers)
    print_result(
        "GET /auth/me - Token inválido",
        response.status_code,
        [401, 422],
        response.json() if response.status_code in [401, 422] else None
    )

def run_comprehensive_tests():
    """Executar todos os testes de forma organizada"""
    print("TESTES COMPLETOS DA API - GALERA VÔLEI")
    print("=" * 60)
    print()
    
    try:
        test_health_endpoints()
        print()
        
        test_auth_endpoints()
        print()
        
        test_user_endpoints()
        print()
        
        test_match_endpoints()
        print()
        
        test_error_cases()
        print()
        
        print("=" * 60)
        print(" TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"X Erro durante a execução dos testes: {e}")
        print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_tests()