@echo off
REM Script para Windows testar a aplicação no Docker

echo === GALERA VOLEI - TESTE DOCKER ===

REM Função para aguardar a API estar pronta
echo Aguardando API estar pronta...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:8000/docs >nul 2>&1
    if !errorlevel! == 0 (
        echo ✓ API está pronta!
        goto test_api
    )
    echo Tentativa %%i/30 - aguardando...
    timeout /t 2 >nul
)
echo ✗ API não ficou pronta a tempo
exit /b 1

:test_api
echo === Testando criação de convite ===

REM 1. Registrar usuário
echo 1. Registrando usuário...
curl -s -X POST "http://localhost:8000/api/v1/auth/register" ^
    -H "Content-Type: application/json" ^
    -d "{\"nome\": \"Docker Test User\", \"email\": \"docker_test@example.com\", \"senha\": \"senha123\"}" ^
    > user_response.json

if %errorlevel% == 0 (
    echo ✓ Usuário registrado
) else (
    echo ✗ Erro ao registrar usuário
    exit /b 1
)

echo 🎉 Teste básico completado! Verifique os logs do Docker para mais detalhes.
del user_response.json >nul 2>&1