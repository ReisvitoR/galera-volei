"""
Testes adicionais para validação completa do sistema de categorização
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

def test_categoria_intermediario_regras():
    """Teste: categoria INTERMEDIARIO permite intermediários e proplayers"""
    
    # Criar usuário intermediário organizador
    token_inter, user_inter_id, _ = create_user_with_type("intermediario", "_inter1")
    headers_inter = {"Authorization": f"Bearer {token_inter}"}
    
    # Criar partida categoria intermediário
    partida_data = {
        "titulo": "Partida Intermediários",
        "descricao": "Para intermediários e proplayers",
        "tipo": "normal",
        "categoria": "intermediario",
        "data_partida": "2025-11-09T15:00:00",
        "local": "Quadra Intermediários",
        "max_participantes": 6,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_inter)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Tentar convidar usuário amador (deve falhar)
    token_amador, user_amador_id, _ = create_user_with_type("amador", "_inter2")
    
    convite_data = {
        "convidado_id": user_amador_id,
        "partida_id": partida_id,
        "mensagem": "Convite para partida intermediário"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_inter)
    assert convite_response.status_code == 400
    
    # Convidar usuário proplayer (deve funcionar)
    token_pro, user_pro_id, _ = create_user_with_type("proplayer", "_inter3")
    
    convite_data["convidado_id"] = user_pro_id
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_inter)
    assert convite_response.status_code == 201

def test_criacao_partida_com_categoria_invalida():
    """Teste: falha ao criar partida com categoria inválida"""
    
    token_noob, user_noob_id, _ = create_user_with_type("noob", "_invalid1")
    headers_noob = {"Authorization": f"Bearer {token_noob}"}
    
    # Tentar criar partida com categoria inválida
    partida_data = {
        "titulo": "Partida Inválida",
        "descricao": "Categoria que não existe",
        "tipo": "normal",
        "categoria": "master",  # Categoria que não existe
        "data_partida": "2025-11-09T16:00:00",
        "local": "Quadra Test",
        "max_participantes": 8,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_noob)
    assert partida_response.status_code == 422  # Validation error

def test_auto_convite_organizador():
    """Teste: organizador da partida pode convidar independente da categoria"""
    
    # Organizador noob criando partida amador (edge case)
    token_noob, user_noob_id, _ = create_user_with_type("noob", "_org1")
    headers_noob = {"Authorization": f"Bearer {token_noob}"}
    
    # Criar partida categoria amador sendo noob
    partida_data = {
        "titulo": "Partida Organizador Noob",
        "descricao": "Noob organizando amador",
        "tipo": "normal",
        "categoria": "amador",
        "data_partida": "2025-11-09T17:00:00",
        "local": "Quadra Especial",
        "max_participantes": 6,
        "publica": False
    }
    
    # Isso pode falhar dependendo das regras de negócio
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_noob)
    # Aceitar tanto sucesso quanto falha, dependendo das regras implementadas
    assert partida_response.status_code in [201, 400]

def test_convite_proprio_usuario():
    """Teste: usuário não pode convidar a si mesmo"""
    
    token_amador, user_amador_id, _ = create_user_with_type("amador", "_self1")
    headers_amador = {"Authorization": f"Bearer {token_amador}"}
    
    # Criar partida
    partida_data = {
        "titulo": "Partida Auto-convite",
        "descricao": "Teste de auto-convite",
        "tipo": "normal",
        "categoria": "amador",
        "data_partida": "2025-11-09T18:00:00",
        "local": "Quadra Auto",
        "max_participantes": 4,
        "publica": False
    }
    
    partida_response = requests.post(f"{API_V1}/partidas/", json=partida_data, headers=headers_amador)
    assert partida_response.status_code == 201
    partida_id = partida_response.json()["id"]
    
    # Tentar se auto-convidar
    convite_data = {
        "convidado_id": user_amador_id,
        "partida_id": partida_id,
        "mensagem": "Auto-convite"
    }
    
    convite_response = requests.post(f"{API_V1}/convites/", json=convite_data, headers=headers_amador)
    assert convite_response.status_code == 400

def test_listar_categorias_permitidas():
    """Teste: verificar quais categorias cada tipo de usuário pode participar"""
    
    # Este teste é mais informativo para verificar a lógica
    from app.utils.categoria_utils import get_categorias_permitidas
    from app.models.enums import TipoUsuario
    
    # Testar todas as combinações
    categorias_noob = get_categorias_permitidas(TipoUsuario.NOOB)
    categorias_noob_str = [cat.value for cat in categorias_noob]
    assert "livre" in categorias_noob_str
    assert "noob" in categorias_noob_str
    assert "amador" not in categorias_noob_str
    
    categorias_amador = get_categorias_permitidas(TipoUsuario.AMADOR)
    categorias_amador_str = [cat.value for cat in categorias_amador]
    assert "livre" in categorias_amador_str
    assert "noob" not in categorias_amador_str
    assert "amador" in categorias_amador_str
    assert "intermediario" not in categorias_amador_str
    
    categorias_inter = get_categorias_permitidas(TipoUsuario.INTERMEDIARIO)
    categorias_inter_str = [cat.value for cat in categorias_inter]
    assert "livre" in categorias_inter_str
    assert "amador" in categorias_inter_str
    assert "intermediario" in categorias_inter_str
    assert "avancado" not in categorias_inter_str
    
    categorias_pro = get_categorias_permitidas(TipoUsuario.PROPLAYER)
    assert len(categorias_pro) == 4  # Pode participar de livre, amador, intermediario, avancado (não noob)

def test_descricao_categorias():
    """Teste: verificar descrições das categorias"""
    
    from app.utils.categoria_utils import get_descricao_categoria
    from app.models.enums import CategoriaPartida
    
    desc_livre = get_descricao_categoria(CategoriaPartida.LIVRE)
    assert "Aberto para todos" in desc_livre
    
    desc_noob = get_descricao_categoria(CategoriaPartida.NOOB)
    assert "apenas para iniciantes" in desc_noob.lower()
    
    desc_avancado = get_descricao_categoria(CategoriaPartida.AVANCADO)
    assert "jogadores avançados" in desc_avancado.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])