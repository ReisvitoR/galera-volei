#!/usr/bin/env python3
"""
Script de teste completo para Docker
"""
import requests
import json
import time
import sys
from datetime import datetime

API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

def wait_for_api(max_attempts=30):
    """Aguarda a API estar disponível"""
    print("🔄 Aguardando API ficar disponível...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE}/", timeout=2)
            if response.status_code == 200:
                print("✅ API disponível!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Tentativa {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ API não ficou disponível")
    return False

def test_complete_flow():
    """Teste do fluxo completo"""
    print("\n🧪 INICIANDO TESTE COMPLETO NO DOCKER")
    print("=" * 50)
    
    # 1. Registrar usuários
    timestamp = int(time.time())
    
    user1_data = {
        "nome": "Docker User 1",
        "email": f"docker1_{timestamp}@test.com",
        "senha": "senha123"
    }
    
    user2_data = {
        "nome": "Docker User 2", 
        "email": f"docker2_{timestamp}@test.com",
        "senha": "senha123"
    }
    
    print("\n1️⃣ Registrando usuários...")
    
    # Registrar usuário 1
    response1 = requests.post(f"{API_V1}/auth/register", json=user1_data)
    print(f"   User 1 - Status: {response1.status_code}")
    if response1.status_code != 201:
        print(f"   ❌ Erro: {response1.text}")
        return False
    
    token1 = response1.json()["access_token"]
    user1_id = response1.json()["user"]["id"]
    
    # Registrar usuário 2
    response2 = requests.post(f"{API_V1}/auth/register", json=user2_data)
    print(f"   User 2 - Status: {response2.status_code}")
    if response2.status_code != 201:
        print(f"   ❌ Erro: {response2.text}")
        return False
    
    user2_id = response2.json()["user"]["id"]
    
    print(f"   ✅ Usuários criados - IDs: {user1_id}, {user2_id}")
    
    # 2. Criar partida privada
    print("\n2️⃣ Criando partida privada...")
    
    partida_data = {
        "titulo": f"Docker Test Match {timestamp}",
        "descricao": "Partida teste no Docker",
        "data_hora": "2024-12-01T18:00:00",
        "local": "Quadra Docker",
        "max_participantes": 10,
        "tipo": "amistoso",
        "publica": False
    }
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    response = requests.post(f"{API_V1}/partidas/", headers=headers1, json=partida_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"   ❌ Erro: {response.text}")
        return False
    
    partida_id = response.json()["id"]
    print(f"   ✅ Partida criada - ID: {partida_id}")
    
    # 3. Criar convite
    print("\n3️⃣ Testando criação de convite...")
    
    convite_data = {
        "convidado_id": user2_id,
        "partida_id": partida_id,
        "mensagem": "Convite teste Docker!"
    }
    
    response = requests.post(f"{API_V1}/convites/", headers=headers1, json=convite_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 201:
        print("   ✅ Convite criado com sucesso!")
        convite_id = response.json()["id"]
        
        # 4. Listar convites
        print("\n4️⃣ Listando convites...")
        response = requests.get(f"{API_V1}/convites/", headers=headers1)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            convites = response.json()
            print(f"   ✅ {len(convites)} convite(s) encontrado(s)")
        
        return True
    else:
        print(f"   ❌ Erro na criação do convite: {response.text}")
        return False

def main():
    """Função principal"""
    print("🐳 TESTE DOCKER - GALERA VÔLEI API")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Aguardar API
    if not wait_for_api():
        sys.exit(1)
    
    # Executar teste
    success = test_complete_flow()
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando 100% no Docker")
        sys.exit(0)
    else:
        print("\n💥 TESTES FALHARAM!")
        sys.exit(1)

if __name__ == "__main__":
    main()