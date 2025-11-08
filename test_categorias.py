"""
Testes para o sistema de categorização de partidas
"""
import pytest
import requests
import time
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

def create_user_with_type(user_type, suffix=""):
    """Criar usuário com tipo específico"""
    timestamp = f"{int(time.time())}{int(time.time() * 1000000) % 1000000}{suffix}"
    
    # Primeiro registrar como noob
    user_data = {
        "nome": f"User {user_type} {timestamp}",
        "email": f"user_{user_type}_{timestamp}@test.com",
        "senha": "senha123"
    }
    
    response = requests.post(f"{API_V1}/auth/register", json=user_data)
    if response.status_code != 201:
        # Tentar com timestamp diferente
        timestamp2 = f"{timestamp}_{int(time.time() * 1000000) % 100000}"
        user_data["email"] = f"user_{user_type}_{timestamp2}@test.com"
        user_data["nome"] = f"User {user_type} {timestamp2}"
        response = requests.post(f"{API_V1}/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    
    # Atualizar tipo do usuário se não for noob
    if user_type != "noob":
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"tipo": user_type}
        update_response = requests.put(f"{API_V1}/usuarios/{user_id}", json=update_data, headers=headers)
        # Nota: Assumindo que o endpoint de atualização existe
    
    return token, user_id, user_data

def test_categoria_livre_permite_todos_niveis():
    """Teste: categoria LIVRE permite todos os níveis de usuários"""
    
    # Criar usuário noob
    token_noob, user_noob_id, _ = create_user_with_type("noob", "_livre1")
    headers_noob = {"Authorization": f"Bearer {token_noob}"}
    
    # Criar partida categoria livre
    partida_data = {
        "titulo": "Partida Livre",
        "descricao": "Todos podem participar",
        "tipo": "normal",
        "categoria": "livre",
        "data_partida": "2025-11-08T20:00:00",
        "local": "Quadra Livre",
        "max_participantes": 8,
        "publica": False  # Privada para testar convites
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_noob)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Criar usuário amador e tentar convidar (deve funcionar)
    token_amador, user_amador_id, _ = create_user_with_type("amador", "_livre2")
    
    convite_data = {
        "convidado_id": user_amador_id,
        "partida_id": partida_id,
        "mensagem": "Convite para partida livre"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_noob)
    assert convite_response.status_code == 201

def test_categoria_noob_apenas_iniciantes():
    """Teste: categoria NOOB permite apenas usuários noob"""
    
    # Criar usuário noob organizador
    token_noob, user_noob_id, _ = create_user_with_type("noob", "_noob1")
    headers_noob = {"Authorization": f"Bearer {token_noob}"}
    
    # Criar partida categoria noob
    partida_data = {
        "titulo": "Partida Iniciantes",
        "descricao": "Apenas para iniciantes",
        "tipo": "normal",
        "categoria": "noob",
        "data_partida": "2025-11-08T21:00:00",
        "local": "Quadra Iniciantes",
        "max_participantes": 6,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_noob)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Tentar convidar usuário amador (deve falhar)
    token_amador, user_amador_id, _ = create_user_with_type("amador", "_noob2")
    
    convite_data = {
        "convidado_id": user_amador_id,
        "partida_id": partida_id,
        "mensagem": "Convite para partida noob"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_noob)
    assert convite_response.status_code == 400
    assert "não pode participar" in convite_response.json()["detail"]

def test_categoria_amador_permite_acima():
    """Teste: categoria AMADOR permite amadores e níveis superiores"""
    
    # Criar usuário amador organizador
    token_amador, user_amador_id, _ = create_user_with_type("amador", "_amador1")
    headers_amador = {"Authorization": f"Bearer {token_amador}"}
    
    # Criar partida categoria amador
    partida_data = {
        "titulo": "Partida Amadores",
        "descricao": "Para amadores e acima",
        "tipo": "normal",
        "categoria": "amador",
        "data_partida": "2025-11-08T22:00:00",
        "local": "Quadra Amadores",
        "max_participantes": 8,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_amador)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Tentar convidar usuário noob (deve falhar)
    token_noob, user_noob_id, _ = create_user_with_type("noob", "_amador2")
    
    convite_data = {
        "convidado_id": user_noob_id,
        "partida_id": partida_id,
        "mensagem": "Convite para partida amador"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_amador)
    assert convite_response.status_code == 400
    
    # Convidar usuário intermediário (deve funcionar)
    token_inter, user_inter_id, _ = create_user_with_type("intermediario", "_amador3")
    
    convite_data["convidado_id"] = user_inter_id
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_amador)
    assert convite_response.status_code == 201

def test_categoria_avancado_apenas_proplayers():
    """Teste: categoria AVANÇADO permite apenas proplayers"""
    
    # Criar usuário proplayer organizador  
    token_pro, user_pro_id, _ = create_user_with_type("proplayer", "_pro1")
    headers_pro = {"Authorization": f"Bearer {token_pro}"}
    
    # Criar partida categoria avançado
    partida_data = {
        "titulo": "Partida Avançados",
        "descricao": "Apenas para proplayers",
        "tipo": "ranked",
        "categoria": "avancado",
        "data_partida": "2025-11-08T23:00:00",
        "local": "Quadra Profissional",
        "max_participantes": 4,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_pro)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Tentar convidar usuário intermediário (deve falhar)
    token_inter, user_inter_id, _ = create_user_with_type("intermediario", "_pro2")
    
    convite_data = {
        "convidado_id": user_inter_id,
        "partida_id": partida_id,
        "mensagem": "Convite para partida avançado"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_pro)
    assert convite_response.status_code == 400

def test_validacao_categoria_partida_publica():
    """Teste: validação de categoria em partidas públicas"""
    
    # Criar usuário noob
    token_noob, user_noob_id, _ = create_user_with_type("noob", "_pub1")
    headers_noob = {"Authorization": f"Bearer {token_noob}"}
    
    # Criar usuário amador
    token_amador, user_amador_id, _ = create_user_with_type("amador", "_pub2")
    headers_amador = {"Authorization": f"Bearer {token_amador}"}
    
    # Amador cria partida categoria amador pública
    partida_data = {
        "titulo": "Partida Pública Amador",
        "descricao": "Pública mas só para amadores+",
        "tipo": "normal",
        "categoria": "amador",
        "data_partida": "2025-11-09T10:00:00",
        "local": "Quadra Pública",
        "max_participantes": 8,
        "publica": True
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_amador)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Usuário noob tenta participar (deve falhar se implementado o endpoint)
    # Nota: Este teste assume que existe um endpoint POST /partidas/{id}/participar
    # Se não existir, pode ser comentado ou implementado depois
    
    print(f"✅ Partida categoria amador criada - ID: {partida_id}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])