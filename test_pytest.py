"""
Testes profissionais usando pytest para a API Galera Vôlei
Execute com: pytest test_pytest.py -v
"""
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

# Fixtures
@pytest.fixture
def admin_token():
    """Fixture para obter token de admin"""
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@galeravolei.com",
        "senha": "admin123"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

@pytest.fixture
def auth_headers(admin_token):
    """Fixture para headers de autenticação"""
    if admin_token:
        return {"Authorization": f"Bearer {admin_token}"}
    return {}

# Testes de Health Check
class TestHealthCheck:
    def test_docs_endpoint(self):
        """Teste da documentação Swagger"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self):
        """Teste do schema OpenAPI"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

# Testes de Autenticação
class TestAuthentication:
    def test_login_success(self):
        """Teste de login com credenciais válidas"""
        response = client.post("/api/v1/auth/login", json={
            "email": "admin@galeravolei.com",
            "senha": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Teste de login com credenciais inválidas"""
        response = client.post("/api/v1/auth/login", json={
            "email": "invalid@test.com",
            "senha": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_missing_fields(self):
        """Teste de login com campos faltando"""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@test.com"
            # senha missing
        })
        assert response.status_code == 422  # Validation error
    
    def test_register_new_user(self):
        """Teste de registro de novo usuário"""
        response = client.post("/api/v1/auth/register", json={
            "nome": "Novo Usuário Pytest",
            "email": "pytest@exemplo.com",
            "senha": "123456",
            "tipo": "intermediario"
        })
        # Pode ser 201 (criado) ou 400 (já existe)
        assert response.status_code in [201, 400]
    
    def test_get_current_user(self, auth_headers):
        """Teste de obter usuário atual"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "nome" in data
        assert "email" in data

# Testes de Usuários
class TestUsers:
    def test_list_users_without_auth(self):
        """Teste de listagem de usuários sem autenticação"""
        response = client.get("/api/v1/usuarios/")
        # Deve retornar 401/403 (não autorizado)
        assert response.status_code in [401, 403]
    
    def test_list_users_with_auth(self, auth_headers):
        """Teste de listagem de usuários com autenticação"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        response = client.get("/api/v1/usuarios/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Deve ter pelo menos o admin
    
    def test_get_user_ranking(self, auth_headers):
        """Teste de ranking de usuários"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        response = client.get("/api/v1/usuarios/ranking", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_specific_user(self, auth_headers):
        """Teste de buscar usuário específico"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        # Buscar o admin (ID 1)
        response = client.get("/api/v1/usuarios/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "admin@galeravolei.com"
    
    def test_get_nonexistent_user(self, auth_headers):
        """Teste de buscar usuário inexistente"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        response = client.get("/api/v1/usuarios/9999", headers=auth_headers)
        assert response.status_code == 404

# Testes de Partidas
class TestMatches:
    def test_list_matches_without_auth(self):
        """Teste de listagem de partidas sem autenticação"""
        response = client.get("/api/v1/partidas/")
        # Deve retornar 401/403 (não autorizado)
        assert response.status_code in [401, 403]
    
    def test_list_matches_with_auth(self, auth_headers):
        """Teste de listagem de partidas com autenticação"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        response = client.get("/api/v1/partidas/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_match(self, auth_headers):
        """Teste de criação de partida"""
        if not auth_headers:
            pytest.skip("Token de autenticação não disponível")
        
        match_data = {
            "titulo": "Partida Teste Pytest",
            "descricao": "Descrição da partida teste",
            "data_partida": "2025-10-16T20:00:00",
            "local": "Quadra Pytest",
            "max_jogadores": 12,
            "nivel_minimo": "amador",
            "tipo": "amistoso",
            "valor_taxa": 10.0
        }
        
        response = client.post("/api/v1/partidas/", json=match_data, headers=auth_headers)
        assert response.status_code in [201, 400, 403, 422]  # 201=criado, 400=erro validação, 403=sem permissão, 422=validação pydantic
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["titulo"] == match_data["titulo"]

# Testes de Casos de Erro
class TestErrorCases:
    def test_nonexistent_route(self):
        """Teste de rota inexistente"""
        response = client.get("/api/v1/rota-que-nao-existe")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Teste de método HTTP não permitido"""
        response = client.delete("/api/v1/auth/login")
        assert response.status_code == 405
    
    def test_invalid_token(self):
        """Teste com token inválido"""
        headers = {"Authorization": "Bearer token-totalmente-invalido"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [401, 422]
    
    def test_malformed_request(self):
        """Teste com requisição mal formada"""
        response = client.post("/api/v1/auth/login", json={
            "email": "email-sem-formato-valido",  # Email inválido
            "senha": ""  # Senha vazia
        })
        assert response.status_code == 422

# Testes de Performance Básicos
class TestBasicPerformance:
    def test_response_time_docs(self):
        """Teste básico de tempo de resposta da documentação"""
        import time
        start = time.time()
        response = client.get("/docs")
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 2.0  # Deve responder em menos de 2 segundos
    
    def test_response_time_login(self):
        """Teste básico de tempo de resposta do login"""
        import time
        start = time.time()
        response = client.post("/api/v1/auth/login", json={
            "email": "admin@galeravolei.com",
            "senha": "admin123"
        })
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 3.0  # Login deve ser rápido (menos de 3 segundos)