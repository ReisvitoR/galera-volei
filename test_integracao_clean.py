"""
Testes de integração para verificar fluxo completo da API
Testar interações entre diferentes componentes do sistema
"""
import pytest
import requests
import time
import json
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

def create_unique_user(suffix=""):
    """Criar usuário único para testes"""
    timestamp = f"{int(time.time())}{int(time.time() * 1000000) % 1000000}{suffix}"
    user_data = {
        "nome": f"Integration User {timestamp}",
        "email": f"integration_{timestamp}@test.com",
        "senha": "senha123"
    }
    
    response = requests.post(f"{API_V1}/auth/register", json=user_data)
    if response.status_code != 201:
        # Tentar com timestamp diferente em caso de colisão
        timestamp2 = f"{timestamp}_{int(time.time() * 1000000) % 100000}"
        user_data["email"] = f"integration_{timestamp2}@test.com"
        user_data["nome"] = f"Integration User {timestamp2}"
        response = requests.post(f"{API_V1}/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    return data["access_token"], data["user"]["id"], user_data

def test_fluxo_completo_convites():
    """Teste: fluxo completo de criação e gerenciamento de convites"""
    
    # 1. Criar usuário organizador
    token_org, user_org_id, user_org_data = create_unique_user("_org")
    headers_org = {"Authorization": f"Bearer {token_org}"}
    
    # 2. Criar usuário convidado
    token_conv, user_conv_id, user_conv_data = create_unique_user("_conv")
    headers_conv = {"Authorization": f"Bearer {token_conv}"}
    
    # 3. Organizador cria partida privada
    partida_data = {
        "titulo": "Partida Integração",
        "descricao": "Teste de integração completo",
        "tipo": "normal",
        "data_partida": "2025-11-08T20:00:00",
        "local": "Quadra Integração",
        "max_participantes": 4,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_org)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # 4. Organizador envia convite
    convite_data = {
        "convidado_id": user_conv_id,
        "partida_id": partida_id,
        "mensagem": "Convite de integração - venha jogar!"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_org)
    assert convite_response.status_code == 201
    convite_id = convite_response.json()["id"]
    assert convite_response.json()["status"] == "pendente"
    
    # 5. Verificar convites enviados pelo organizador
    convites_enviados = requests.get(f"{API_V1}/convites/enviados", headers=headers_org)
    assert convites_enviados.status_code == 200
    assert len(convites_enviados.json()) >= 1
    
    # 6. Verificar convites recebidos pelo convidado
    convites_recebidos = requests.get(f"{API_V1}/convites/recebidos", headers=headers_conv)
    assert convites_recebidos.status_code == 200
    assert len(convites_recebidos.json()) >= 1
    
    # 7. Convidado aceita o convite
    aceitar_response = requests.put(f"{API_V1}/convites/{convite_id}/aceitar", headers=headers_conv)
    assert aceitar_response.status_code == 200
    assert aceitar_response.json()["status"] == "aceito"
    
    # 8. Verificar que convidado foi adicionado à partida
    partida_atualizada = requests.get(f"{API_V1}/partidas/{partida_id}", headers=headers_org)
    assert partida_atualizada.status_code == 200
    participantes = partida_atualizada.json()["participantes"]
    user_ids = [p["id"] for p in participantes]
    assert user_conv_id in user_ids

def test_fluxo_registro_login_criacao_partida():
    """Teste: fluxo de registro, login e criação de partida"""
    
    # 1. Registrar usuário
    token, user_id, user_data = create_unique_user("_flow")
    
    # 2. Fazer login com as mesmas credenciais
    login_data = {
        "email": user_data["email"],
        "senha": user_data["senha"]
    }
    
    login_response = requests.post(f"{API_V1}/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_token = login_response.json()["access_token"]
    
    # 3. Usar token do login para criar partida
    headers = {"Authorization": f"Bearer {login_token}"}
    
    partida_data = {
        "titulo": "Partida Pós Login",
        "descricao": "Teste após login",
        "tipo": "normal",
        "data_partida": "2025-11-08T21:00:00",
        "local": "Quadra Login",
        "max_participantes": 6,
        "publica": True
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers)
    assert partida_response.status_code == 201
    assert partida_response.json()["organizador_id"] == user_id

def test_listar_partidas_publicas_privadas():
    """Teste: verificar listagem de partidas públicas e privadas"""
    
    # Criar usuário
    token, user_id, _ = create_unique_user("_list")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar partida pública
    partida_publica = {
        "titulo": "Partida Pública Teste",
        "descricao": "Teste",
        "tipo": "normal",
        "data_partida": "2025-11-08T22:00:00",
        "local": "Quadra Pública",
        "max_participantes": 8,
        "publica": True
    }
    
    pub_response = requests.post(f"{API_V1}/partidas/", json=partida_publica, headers=headers)
    assert pub_response.status_code == 201
    
    # Criar partida privada
    partida_privada = {
        "titulo": "Partida Privada Teste",
        "descricao": "Teste",
        "tipo": "normal",
        "data_partida": "2025-11-08T23:00:00",
        "local": "Quadra Privada",
        "max_participantes": 4,
        "publica": False
    }
    
    priv_response = requests.post(f"{API_V1}/partidas/", json=partida_privada, headers=headers)
    assert priv_response.status_code == 201
    
    # Listar todas as partidas
    partidas_response = requests.get(f"{API_V1}/partidas/", headers=headers)
    assert partidas_response.status_code == 200
    partidas = partidas_response.json()
    assert len(partidas) >= 2

def test_verificar_permissoes_convites():
    """Teste: verificar permissões corretas para convites"""
    
    # Criar dois usuários
    token1, user1_id, _ = create_unique_user("_perm1")
    token2, user2_id, _ = create_unique_user("_perm2")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Usuário 1 cria partida privada
    partida_data = {
        "titulo": "Partida Permissões",
        "descricao": "Teste de permissões",
        "tipo": "normal",
        "data_partida": "2025-11-09T10:00:00",
        "local": "Quadra Permissões",
        "max_participantes": 4,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers1)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Usuário 2 tenta enviar convite para partida do usuário 1 (deve falhar)
    convite_data = {
        "convidado_id": user1_id,
        "partida_id": partida_id,
        "mensagem": "Convite não autorizado"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers2)
    assert convite_response.status_code == 403  # Forbidden

if __name__ == "__main__":
    pytest.main([__file__, "-v"])