"""
Teste do endpoint de debug
"""
import requests
import json
from datetime import datetime, timedelta
import time

API_BASE = "http://127.0.0.1:8000"
API_V1 = f"{API_BASE}/api/v1"

def test_debug_endpoint():
    """Teste do endpoint de debug"""
    
    # 1. Registrar usuário
    user_data = {
        "nome": "Debug User",
        "email": f"debug_{int(time.time())}@test.com",
        "senha": "senha123"
    }
    
    response = requests.post(f"{API_V1}/auth/register", json=user_data)
    print(f"Registro - Status: {response.status_code}")
    if response.status_code != 201:
        print(f"Erro no registro: {response.text}")
        return
    
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]
    print(f"Usuário registrado - ID: {user_id}")
    
    # 2. Testar endpoint de debug
    headers = {"Authorization": f"Bearer {token}"}
    convite_data = {
        "convidado_id": 1,
        "partida_id": 1,
        "mensagem": "Debug test"
    }
    
    print(f"Testando endpoint debug...")
    try:
        response = requests.post(f"{API_V1}/convites/debug", headers=headers, json=convite_data, timeout=10)
        print(f"Debug endpoint - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint de debug funcionando!")
        else:
            print(f"❌ Erro no debug: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_debug_endpoint()