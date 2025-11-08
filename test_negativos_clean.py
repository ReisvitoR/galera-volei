"""
Testes negativos para verificar casos de erro da API
Verificar se a API responde corretamente a dados inválidos
"""
import pytest
import requests
import time
import json
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

def setup_test_user():
    """Criar usuário de teste e retornar token"""
    # Usar timestamp mais randômico para evitar colisões
    timestamp = f"{int(time.time())}{int(time.time() * 1000000) % 1000000}"
    user_data = {
        "nome": f"Test User {timestamp}",
        "email": f"test_{timestamp}@test.com",
        "senha": "senha123"
    }
    
    response = requests.post(f"{API_V1}/auth/register", json=user_data)
    
    # Se falhar por email duplicado, tentar com outro timestamp
    if response.status_code == 400:
        timestamp2 = f"{timestamp}_{int(time.time() * 1000000) % 100000}"
        user_data["email"] = f"test_{timestamp2}@test.com"
        user_data["nome"] = f"Test User {timestamp2}"
        response = requests.post(f"{API_V1}/auth/register", json=user_data)
    
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    
    data = response.json()
    return data["access_token"], data["user"]["id"]

def test_convite_sem_token():
    """Teste: tentar criar convite sem autenticação"""
    convite_data = {
        "convidado_id": 1,
        "partida_id": 1,
        "mensagem": "Teste sem token"
    }
    
    response = requests.post(f"{API_V1}/convites/", json=convite_data)
    assert response.status_code == 403  # Forbidden instead of 401

def test_convite_token_invalido():
    """Teste: tentar criar convite com token inválido"""
    headers = {"Authorization": "Bearer token_invalido"}
    convite_data = {
        "convidado_id": 1,
        "partida_id": 1,
        "mensagem": "Teste token inválido"
    }
    
    response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers)
    assert response.status_code == 401

def test_convite_dados_invalidos():
    """Teste: criar convite com dados inválidos"""
    token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste com convidado_id inválido
    convite_data = {
        "convidado_id": "invalid",
        "partida_id": 1,
        "mensagem": "Teste"
    }
    
    response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers)
    assert response.status_code == 422  # Validation error

def test_convite_partida_inexistente():
    """Teste: criar convite para partida que não existe"""
    token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    convite_data = {
        "convidado_id": 1,
        "partida_id": 99999,  # ID que não existe
        "mensagem": "Teste partida inexistente"
    }
    
    response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers)
    assert response.status_code == 404

def test_convite_usuario_inexistente():
    """Teste: criar convite para usuário que não existe"""
    token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar partida privada primeiro
    partida_data = {
        "titulo": "Partida Teste Negativo",
        "descricao": "Teste",
        "tipo": "normal",
        "data_partida": "2025-11-08T20:00:00",
        "local": "Local Teste",
        "max_participantes": 4,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Tentar convidar usuário inexistente
    convite_data = {
        "convidado_id": 99999,  # ID que não existe
        "partida_id": partida_id,
        "mensagem": "Teste usuário inexistente"
    }
    
    response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers)
    assert response.status_code == 404

def test_registrar_usuario_email_duplicado():
    """Teste: tentar registrar usuário com email já existente"""
    # Usar timestamp único para evitar conflitos com outros testes
    timestamp = f"dup_{int(time.time())}{int(time.time() * 1000000) % 1000000}"
    email_duplicado = f"{timestamp}@test.com"
    
    # Primeiro usuário
    user_data = {
        "nome": "Primeiro Usuario",
        "email": email_duplicado,
        "senha": "senha123"
    }
    
    response1 = requests.post(f"{API_V1}/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Tentar registrar com mesmo email
    user_data2 = {
        "nome": "Segundo Usuario",
        "email": email_duplicado,  # Email duplicado
        "senha": "outra_senha"
    }
    
    response2 = requests.post(f"{API_V1}/auth/register", json=user_data2)
    assert response2.status_code == 400

def test_login_credenciais_invalidas():
    """Teste: tentar fazer login com credenciais inválidas"""
    login_data = {
        "email": "inexistente@test.com",
        "senha": "senha_errada"
    }
    
    response = requests.post(f"{API_V1}/auth/login", json=login_data)
    assert response.status_code == 401

def test_criar_partida_sem_token():
    """Teste: tentar criar partida sem autenticação"""
    partida_data = {
        "titulo": "Partida Sem Auth",
        "descricao": "Teste",
        "tipo": "normal",
        "data_partida": "2025-11-08T20:00:00",
        "local": "Local",
        "max_participantes": 4,
        "publica": True
    }
    
    response = requests.post(f"{API_V1}/partidas/", json=partida_data)
    assert response.status_code == 403  # Forbidden instead of 401

def test_partida_dados_invalidos():
    """Teste: criar partida com dados inválidos"""
    token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste sem campo obrigatório 'tipo'
    partida_data = {
        "titulo": "Partida Inválida",
        "descricao": "Teste",
        # "tipo": "normal",  # Campo obrigatório omitido
        "data_partida": "2025-11-08T20:00:00",
        "local": "Local",
        "max_participantes": 4,
        "publica": True
    }
    
    response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers)
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])