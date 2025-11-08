"""
Script para testar o sistema completo de convites
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_convite_system():
    print("🚀 Iniciando teste completo do sistema de convites\n")
    
    # Dados de teste
    organizador_data = {
        "nome": "Organizador Teste",
        "email": "organizador@test.com",
        "senha": "123456"
    }
    
    convidado_data = {
        "nome": "Convidado Teste", 
        "email": "convidado@test.com",
        "senha": "123456"
    }
    
    # Registrar usuários
    print("👤 Registrando usuários...")
    org_response = requests.post(f"{API_BASE}/auth/register", json=organizador_data)
    conv_response = requests.post(f"{API_BASE}/auth/register", json=convidado_data)
    
    if org_response.status_code != 201:
        print("⚠️  Organizador já existe, tentando login...")
        org_response = requests.post(f"{API_BASE}/auth/login", 
                                   data={"username": organizador_data["email"], "password": organizador_data["senha"]})
    
    if conv_response.status_code != 201:
        print("⚠️  Convidado já existe, tentando login...")
        conv_response = requests.post(f"{API_BASE}/auth/login",
                                    data={"username": convidado_data["email"], "password": convidado_data["senha"]})
    
    # Obter tokens
    if org_response.status_code in [200, 201]:
        if "access_token" in org_response.json():
            org_token = org_response.json()["access_token"]
        else:
            print("❌ Erro ao obter token do organizador")
            return
    else:
        print(f"❌ Erro no login do organizador: {org_response.text}")
        return
    
    if conv_response.status_code in [200, 201]:
        if "access_token" in conv_response.json():
            conv_token = conv_response.json()["access_token"]
        else:
            print("❌ Erro ao obter token do convidado")
            return
    else:
        print(f"❌ Erro no login do convidado: {conv_response.text}")
        return
    
    print("✅ Usuários autenticados com sucesso!")
    
    # Headers de autenticação
    org_headers = {"Authorization": f"Bearer {org_token}"}
    conv_headers = {"Authorization": f"Bearer {conv_token}"}
    
    # Criar partida privada
    print("\n🏐 Criando partida privada...")
    partida_data = {
        "titulo": "Partida Privada - Teste Convites",
        "descricao": "Partida para testar sistema de convites",
        "data_hora": (datetime.now() + timedelta(days=1)).isoformat(),
        "local": "Quadra Teste",
        "max_participantes": 12,
        "publica": False  # Partida privada
    }
    
    partida_response = requests.post(f"{API_BASE}/partidas/", 
                                   json=partida_data, 
                                   headers=org_headers)
    
    if partida_response.status_code == 201:
        partida_id = partida_response.json()["id"]
        print(f"✅ Partida privada criada com ID: {partida_id}")
    else:
        print(f"❌ Erro ao criar partida: {partida_response.text}")
        return
    
    # Obter ID do convidado
    print("\n👥 Obtendo dados dos usuários...")
    convidado_profile = requests.get(f"{API_BASE}/usuarios/me", headers=conv_headers)
    if convidado_profile.status_code == 200:
        convidado_id = convidado_profile.json()["id"]
        print(f"✅ ID do convidado: {convidado_id}")
    else:
        print(f"❌ Erro ao obter perfil do convidado: {convidado_profile.text}")
        return
    
    # Enviar convite
    print("\n📩 Enviando convite...")
    convite_data = {
        "mensagem": "Olá! Você está convidado para jogar vôlei conosco!",
        "data_expiracao": (datetime.now() + timedelta(days=7)).isoformat(),
        "convidado_id": convidado_id,
        "partida_id": partida_id
    }
    
    convite_response = requests.post(f"{API_BASE}/convites/", 
                                   json=convite_data, 
                                   headers=org_headers)
    
    if convite_response.status_code == 201:
        convite_id = convite_response.json()["id"]
        print(f"✅ Convite enviado com ID: {convite_id}")
        print(f"   Mensagem: {convite_response.json()['mensagem']}")
        print(f"   Status: {convite_response.json()['status']}")
    else:
        print(f"❌ Erro ao enviar convite: {convite_response.text}")
        return
    
    # Listar convites recebidos
    print("\n📬 Verificando convites recebidos pelo convidado...")
    convites_recebidos = requests.get(f"{API_BASE}/convites/recebidos", headers=conv_headers)
    
    if convites_recebidos.status_code == 200:
        convites = convites_recebidos.json()
        print(f"✅ {len(convites)} convite(s) encontrado(s)")
        for convite in convites:
            print(f"   - ID: {convite['id']}, Status: {convite['status']}")
    else:
        print(f"❌ Erro ao listar convites recebidos: {convites_recebidos.text}")
    
    # Aceitar convite
    print("\n✅ Aceitando convite...")
    aceitar_response = requests.put(f"{API_BASE}/convites/{convite_id}/aceitar", 
                                  headers=conv_headers)
    
    if aceitar_response.status_code == 200:
        convite_aceito = aceitar_response.json()
        print(f"✅ Convite aceito! Status: {convite_aceito['status']}")
    else:
        print(f"❌ Erro ao aceitar convite: {aceitar_response.text}")
    
    # Verificar se o usuário foi adicionado à partida
    print("\n🏐 Verificando participantes da partida...")
    partida_detalhes = requests.get(f"{API_BASE}/partidas/{partida_id}", headers=org_headers)
    
    if partida_detalhes.status_code == 200:
        participantes = partida_detalhes.json().get("participantes", [])
        print(f"✅ Partida tem {len(participantes)} participante(s)")
        for participante in participantes:
            print(f"   - {participante['nome']} ({participante['email']})")
    else:
        print(f"❌ Erro ao obter detalhes da partida: {partida_detalhes.text}")
    
    # Testar endpoints adicionais
    print("\n📊 Testando endpoints adicionais...")
    
    # Convites enviados
    enviados = requests.get(f"{API_BASE}/convites/enviados", headers=org_headers)
    if enviados.status_code == 200:
        print(f"✅ Organizador enviou {len(enviados.json())} convite(s)")
    
    # Convites da partida
    convites_partida = requests.get(f"{API_BASE}/convites/partida/{partida_id}", headers=org_headers)
    if convites_partida.status_code == 200:
        print(f"✅ Partida tem {len(convites_partida.json())} convite(s)")
    
    print("\n🎉 Teste do sistema de convites concluído com sucesso!")
    
    return {
        "partida_id": partida_id,
        "convite_id": convite_id,
        "organizador_token": org_token,
        "convidado_token": conv_token
    }

if __name__ == "__main__":
    try:
        result = test_convite_system()
        print(f"\n📋 IDs criados no teste:")
        if result:
            print(f"   - Partida: {result['partida_id']}")
            print(f"   - Convite: {result['convite_id']}")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")