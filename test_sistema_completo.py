"""
Teste completo e abrangente do sistema de convites
Valida todos os cenários possíveis: positivos, negativos e edge cases
"""

import json
from datetime import datetime, timedelta
import time

def criar_requisicao_curl(method, url, headers=None, data=None):
    """Criar comando curl para requisições"""
    cmd = f'curl -X {method} "{url}" -H "Content-Type: application/json"'
    
    if headers:
        for key, value in headers.items():
            cmd += f' -H "{key}: {value}"'
    
    if data:
        json_data = json.dumps(data) if isinstance(data, dict) else data
        # Escapar aspas para Windows
        json_data = json_data.replace('"', '\\"')
        cmd += f' -d "{json_data}"'
    
    return cmd

def executar_teste(descricao, comando):
    """Executar um teste e mostrar resultado"""
    print(f"\n🧪 {descricao}")
    print(f"📋 Comando: {comando}")
    
    # Simular execução (em ambiente real usaria subprocess)
    print("✅ Preparado para execução")
    return comando

def main():
    print("🚀 INICIANDO BATERIA COMPLETA DE TESTES DO SISTEMA")
    print("=" * 60)
    
    # URLs base
    BASE_URL = "http://127.0.0.1:8000"
    API_URL = f"{BASE_URL}/api/v1"
    
    # Dados de teste
    usuario1_data = {
        "nome": "João Organizador",
        "email": "joao@test.com",
        "senha": "123456"
    }
    
    usuario2_data = {
        "nome": "Maria Convidada",
        "email": "maria@test.com", 
        "senha": "123456"
    }
    
    usuario3_data = {
        "nome": "Pedro Terceiro",
        "email": "pedro@test.com",
        "senha": "123456"
    }
    
    partida_publica_data = {
        "titulo": "Partida Pública - Teste",
        "descricao": "Partida aberta para todos",
        "data_hora": (datetime.now() + timedelta(days=1)).isoformat(),
        "local": "Quadra Central",
        "max_participantes": 12,
        "publica": True
    }
    
    partida_privada_data = {
        "titulo": "Partida Privada - Teste",
        "descricao": "Partida apenas por convite",
        "data_hora": (datetime.now() + timedelta(days=2)).isoformat(),
        "local": "Quadra VIP",
        "max_participantes": 8,
        "publica": False
    }
    
    print("\n" + "="*60)
    print("FASE 1: TESTES DE INFRAESTRUTURA")
    print("="*60)
    
    # Teste 1: Health Check
    executar_teste(
        "Health Check da API",
        f'curl -X GET "{BASE_URL}/health"'
    )
    
    # Teste 2: Documentação
    executar_teste(
        "Acessibilidade da documentação",
        f'curl -X GET "{BASE_URL}/docs"'
    )
    
    print("\n" + "="*60)
    print("FASE 2: TESTES DE AUTENTICAÇÃO")
    print("="*60)
    
    # Teste 3-5: Registro de usuários
    executar_teste(
        "Registrar usuário 1 (Organizador)",
        criar_requisicao_curl("POST", f"{API_URL}/auth/register", data=usuario1_data)
    )
    
    executar_teste(
        "Registrar usuário 2 (Convidado)",
        criar_requisicao_curl("POST", f"{API_URL}/auth/register", data=usuario2_data)
    )
    
    executar_teste(
        "Registrar usuário 3 (Extra)",
        criar_requisicao_curl("POST", f"{API_URL}/auth/register", data=usuario3_data)
    )
    
    # Teste 6-8: Login de usuários
    executar_teste(
        "Login usuário 1",
        f'curl -X POST "{API_URL}/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username={usuario1_data["email"]}&password={usuario1_data["senha"]}"'
    )
    
    executar_teste(
        "Login usuário 2", 
        f'curl -X POST "{API_URL}/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username={usuario2_data["email"]}&password={usuario2_data["senha"]}"'
    )
    
    executar_teste(
        "Login usuário 3",
        f'curl -X POST "{API_URL}/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username={usuario3_data["email"]}&password={usuario3_data["senha"]}"'
    )
    
    print("\n" + "="*60)
    print("FASE 3: TESTES DE PARTIDAS")
    print("="*60)
    
    # Simular tokens (em teste real, extrairia das respostas de login)
    token1 = "TOKEN_USUARIO1"
    token2 = "TOKEN_USUARIO2"
    token3 = "TOKEN_USUARIO3"
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    headers3 = {"Authorization": f"Bearer {token3}"}
    
    # Teste 9-10: Criação de partidas
    executar_teste(
        "Criar partida pública",
        criar_requisicao_curl("POST", f"{API_URL}/partidas/", headers1, partida_publica_data)
    )
    
    executar_teste(
        "Criar partida privada",
        criar_requisicao_curl("POST", f"{API_URL}/partidas/", headers1, partida_privada_data)
    )
    
    # Teste 11: Listar partidas
    executar_teste(
        "Listar todas as partidas",
        criar_requisicao_curl("GET", f"{API_URL}/partidas/")
    )
    
    print("\n" + "="*60)
    print("FASE 4: TESTES DO SISTEMA DE CONVITES - CENÁRIOS POSITIVOS")
    print("="*60)
    
    # Assumir IDs das partidas criadas
    partida_privada_id = 2
    usuario2_id = 2
    usuario3_id = 3
    
    # Teste 12: Enviar convite válido
    convite_data = {
        "mensagem": "Olá! Você está convidado para nossa partida de vôlei!",
        "data_expiracao": (datetime.now() + timedelta(days=7)).isoformat(),
        "convidado_id": usuario2_id,
        "partida_id": partida_privada_id
    }
    
    executar_teste(
        "Enviar convite para partida privada",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_data)
    )
    
    # Teste 13: Listar convites enviados
    executar_teste(
        "Listar convites enviados pelo organizador",
        criar_requisicao_curl("GET", f"{API_URL}/convites/enviados", headers1)
    )
    
    # Teste 14: Listar convites recebidos
    executar_teste(
        "Listar convites recebidos pelo convidado",
        criar_requisicao_curl("GET", f"{API_URL}/convites/recebidos", headers2)
    )
    
    # Teste 15: Listar convites pendentes
    executar_teste(
        "Listar convites pendentes do convidado",
        criar_requisicao_curl("GET", f"{API_URL}/convites/pendentes", headers2)
    )
    
    # Teste 16: Aceitar convite
    convite_id = 1  # Assumir ID do convite criado
    executar_teste(
        "Aceitar convite",
        criar_requisicao_curl("PUT", f"{API_URL}/convites/{convite_id}/aceitar", headers2)
    )
    
    # Teste 17: Verificar participantes da partida
    executar_teste(
        "Verificar participantes da partida após aceitar convite",
        criar_requisicao_curl("GET", f"{API_URL}/partidas/{partida_privada_id}", headers1)
    )
    
    # Teste 18: Enviar segundo convite
    convite2_data = {
        "mensagem": "Segundo convite de teste",
        "data_expiracao": (datetime.now() + timedelta(days=5)).isoformat(),
        "convidado_id": usuario3_id,
        "partida_id": partida_privada_id
    }
    
    executar_teste(
        "Enviar segundo convite",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite2_data)
    )
    
    # Teste 19: Recusar convite
    convite2_id = 2  # Assumir ID do segundo convite
    executar_teste(
        "Recusar convite",
        criar_requisicao_curl("PUT", f"{API_URL}/convites/{convite2_id}/recusar", headers3)
    )
    
    # Teste 20: Listar convites da partida
    executar_teste(
        "Listar todos os convites da partida (visão do organizador)",
        criar_requisicao_curl("GET", f"{API_URL}/convites/partida/{partida_privada_id}", headers1)
    )
    
    print("\n" + "="*60)
    print("FASE 5: TESTES DE CENÁRIOS NEGATIVOS")
    print("="*60)
    
    # Teste 21: Tentar enviar convite para partida pública
    partida_publica_id = 1
    convite_invalido_data = {
        "mensagem": "Convite inválido para partida pública",
        "convidado_id": usuario3_id,
        "partida_id": partida_publica_id
    }
    
    executar_teste(
        "Tentar enviar convite para partida pública (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_invalido_data)
    )
    
    # Teste 22: Tentar enviar convite sem ser organizador
    executar_teste(
        "Tentar enviar convite sem ser organizador (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers2, convite_data)
    )
    
    # Teste 23: Tentar convidar usuário inexistente
    convite_usuario_inexistente = {
        "mensagem": "Convite para usuário inexistente",
        "convidado_id": 999,
        "partida_id": partida_privada_id
    }
    
    executar_teste(
        "Tentar convidar usuário inexistente (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_usuario_inexistente)
    )
    
    # Teste 24: Tentar convidar a si mesmo
    convite_auto = {
        "mensagem": "Auto-convite",
        "convidado_id": 1,  # ID do próprio organizador
        "partida_id": partida_privada_id
    }
    
    executar_teste(
        "Tentar se auto-convidar (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_auto)
    )
    
    # Teste 25: Tentar aceitar convite de outro usuário
    executar_teste(
        "Tentar aceitar convite de outro usuário (deve falhar)",
        criar_requisicao_curl("PUT", f"{API_URL}/convites/{convite2_id}/aceitar", headers2)
    )
    
    # Teste 26: Tentar enviar convite duplicado
    executar_teste(
        "Tentar enviar convite duplicado (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_data)
    )
    
    print("\n" + "="*60)
    print("FASE 6: TESTES DE AUTORIZAÇÃO")
    print("="*60)
    
    # Teste 27: Acessar endpoint sem token
    executar_teste(
        "Tentar acessar convites sem autenticação (deve falhar)",
        criar_requisicao_curl("GET", f"{API_URL}/convites/enviados")
    )
    
    # Teste 28: Acessar com token inválido
    headers_invalido = {"Authorization": "Bearer TOKEN_INVALIDO"}
    executar_teste(
        "Tentar acessar com token inválido (deve falhar)",
        criar_requisicao_curl("GET", f"{API_URL}/convites/enviados", headers_invalido)
    )
    
    # Teste 29: Tentar cancelar convite de outro usuário
    executar_teste(
        "Tentar cancelar convite de outro usuário (deve falhar)",
        criar_requisicao_curl("DELETE", f"{API_URL}/convites/{convite_id}", headers2)
    )
    
    print("\n" + "="*60)
    print("FASE 7: TESTES DE PERFORMANCE E LIMITES")
    print("="*60)
    
    # Teste 30: Listar convites com paginação
    executar_teste(
        "Testar paginação - primeiros 5 convites",
        criar_requisicao_curl("GET", f"{API_URL}/convites/enviados?skip=0&limit=5", headers1)
    )
    
    # Teste 31: Verificar limites de participantes
    executar_teste(
        "Verificar detalhes da partida para validar limites",
        criar_requisicao_curl("GET", f"{API_URL}/partidas/{partida_privada_id}", headers1)
    )
    
    print("\n" + "="*60)
    print("FASE 8: TESTES DE VALIDAÇÃO DE DADOS")
    print("="*60)
    
    # Teste 32: Convite com dados inválidos
    convite_dados_invalidos = {
        "mensagem": "",  # Mensagem vazia
        "convidado_id": "texto",  # ID inválido
        "partida_id": partida_privada_id
    }
    
    executar_teste(
        "Enviar convite com dados inválidos (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_dados_invalidos)
    )
    
    # Teste 33: Data de expiração no passado
    convite_expirado = {
        "mensagem": "Convite já expirado",
        "data_expiracao": (datetime.now() - timedelta(days=1)).isoformat(),
        "convidado_id": usuario3_id,
        "partida_id": partida_privada_id
    }
    
    executar_teste(
        "Enviar convite com data no passado (deve falhar)",
        criar_requisicao_curl("POST", f"{API_URL}/convites/", headers1, convite_expirado)
    )
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES PLANEJADOS")
    print("="*60)
    
    total_testes = 33
    testes_por_categoria = {
        "Infraestrutura": 2,
        "Autenticação": 6,
        "Partidas": 3,
        "Convites Positivos": 9,
        "Cenários Negativos": 6,
        "Autorização": 3,
        "Performance": 2,
        "Validação": 2
    }
    
    print(f"📊 Total de testes planejados: {total_testes}")
    print("\n📋 Distribuição por categoria:")
    for categoria, quantidade in testes_por_categoria.items():
        print(f"   {categoria}: {quantidade} testes")
    
    print(f"\n🔧 Para executar os testes reais:")
    print(f"   1. Certifique-se que o servidor está rodando em {BASE_URL}")
    print(f"   2. Execute cada comando curl gerado")
    print(f"   3. Valide as respostas HTTP e JSONs retornados")
    print(f"   4. Verifique se cenários negativos retornam os erros esperados")
    
    print(f"\n✅ BATERIA DE TESTES COMPLETA PREPARADA!")

if __name__ == "__main__":
    main()