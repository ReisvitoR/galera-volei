"""
Teste direto do endpoint de convites para debug
"""
import requests
import json
from datetime import datetime, timedelta
import time

API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

def test_convite_endpoint():
    """Teste direto do endpoint de convites"""
    
    # 1. Registrar usuário mandante
    mandante_data = {
        "nome": "Mandante Debug",
        "email": f"mandante_debug_{int(time.time())}@test.com",
        "senha": "senha123"
    }
    
    response = requests.post(f"{API_V1}/auth/register", json=mandante_data)
    print(f"Registro mandante - Status: {response.status_code}")
    if response.status_code != 201:
        print(f"Erro no registro: {response.text}")
        return
    
    mandante_token = response.json()["access_token"]
    mandante_id = response.json()["user"]["id"]
    print(f"Mandante registrado - ID: {mandante_id}")
    
    # 2. Registrar usuário convidado
    convidado_data = {
        "nome": "Convidado Debug",
        "email": f"convidado_debug_{int(time.time())}@test.com",
        "senha": "senha123"
    }
    
    response = requests.post(f"{API_V1}/auth/register", json=convidado_data)
    print(f"Registro convidado - Status: {response.status_code}")
    if response.status_code != 201:
        print(f"Erro no registro: {response.text}")
        return
    
    convidado_id = response.json()["user"]["id"]
    print(f"Convidado registrado - ID: {convidado_id}")
    
    # 3. Criar partida privada
    headers = {"Authorization": f"Bearer {mandante_token}"}
    partida_data = {
        "titulo": "Partida Debug",
        "descricao": "Partida para debug",
        "tipo": "normal",
        "data_partida": (datetime.now() + timedelta(days=1)).isoformat(),
        "local": "Quadra Debug",
        "max_participantes": 12,
        "publica": False
    }
    
    response = requests.post(f"{API_V1}/partidas/", headers=headers, json=partida_data)
    print(f"Criação partida - Status: {response.status_code}")
    if response.status_code != 201:
        print(f"Erro na criação: {response.text}")
        return
    
    partida_id = response.json()["id"]
    print(f"Partida criada - ID: {partida_id}")
    
    # 4. Enviar convite
    convite_data = {
        "convidado_id": convidado_id,
        "partida_id": partida_id,
        "mensagem": "Venha jogar!"
    }
    
    print(f"Enviando convite: {convite_data}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(f"{API_V1}/convites/", headers=headers, json=convite_data, timeout=10)
        print(f"Envio convite - Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Convite enviado com sucesso!")
            print(f"Response JSON: {response.json()}")
        else:
            print(f"❌ Erro no envio: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_convite_endpoint()