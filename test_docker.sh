#!/bin/bash

# Script para testar a aplicação no Docker
echo "=== GALERA VOLEI - TESTE DOCKER ==="

# Função para aguardar a API estar pronta
wait_for_api() {
    echo "Aguardando API estar pronta..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
            echo "✅ API está pronta!"
            return 0
        fi
        echo "Tentativa $i/30 - aguardando..."
        sleep 2
    done
    echo "❌ API não ficou pronta a tempo"
    return 1
}

# Função para testar endpoint específico
test_convite_creation() {
    echo "=== Testando criação de convite ==="
    
    # 1. Registrar usuário
    echo "1. Registrando usuário..."
    user_response=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "nome": "Docker Test User",
            "email": "docker_test@example.com",
            "senha": "senha123"
        }')
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Usuário registrado"
        token=$(echo $user_response | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        if [[ -n "$token" ]]; then
            echo "✅ Token obtido: ${token:0:20}..."
        else
            echo "❌ Erro ao obter token"
            echo "Response: $user_response"
            return 1
        fi
    else
        echo "❌ Erro ao registrar usuário"
        return 1
    fi
    
    # 2. Criar partida privada
    echo "2. Criando partida privada..."
    partida_response=$(curl -s -X POST "http://localhost:8000/api/v1/partidas/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d '{
            "titulo": "Partida Docker Test",
            "descricao": "Teste de partida privada no Docker",
            "tipo": "normal",
            "data_partida": "2025-11-08T20:00:00",
            "local": "Quadra Docker",
            "max_participantes": 4,
            "publica": false
        }')
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Partida criada"
        partida_id=$(echo $partida_response | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
        if [[ -n "$partida_id" ]]; then
            echo "✅ ID da partida: $partida_id"
        else
            echo "❌ Erro ao obter ID da partida"
            echo "Response: $partida_response"
            return 1
        fi
    else
        echo "❌ Erro ao criar partida"
        return 1
    fi
    
    # 3. Tentar criar convite
    echo "3. Criando convite..."
    convite_response=$(curl -s -X POST "http://localhost:8000/api/v1/convites/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d "{
            \"convidado_id\": 1,
            \"partida_id\": $partida_id,
            \"mensagem\": \"Convite teste Docker\"
        }")
    
    echo "Response do convite: $convite_response"
    
    if echo "$convite_response" | grep -q '"id"'; then
        echo "✅ Convite criado com sucesso!"
        return 0
    else
        echo "❌ Erro ao criar convite"
        echo "Response: $convite_response"
        return 1
    fi
}

# Execução principal
if wait_for_api; then
    test_convite_creation
    if [[ $? -eq 0 ]]; then
        echo "🎉 SUCESSO: Todos os testes passaram!"
        exit 0
    else
        echo "💥 FALHA: Alguns testes falharam"
        exit 1
    fi
else
    echo "💥 FALHA: API não ficou pronta"
    exit 1
fi