@echo off
echo 🐍 SETUP AMBIENTE LIMPO - GALERA VOLEI API
echo ============================================

:: Limpar ambiente anterior
if exist ".venv_clean" (
    echo 🧹 Removendo ambiente anterior...
    rmdir /s /q ".venv_clean"
)

:: Criar novo ambiente virtual
echo 🔧 Criando ambiente virtual limpo...
python -m venv .venv_clean

:: Ativar ambiente
echo 🔄 Ativando ambiente...
call .venv_clean\Scripts\activate.bat

:: Atualizar pip
echo 📦 Atualizando pip...
python -m pip install --upgrade pip

:: Instalar dependências
echo 📋 Instalando dependências...
pip install -r requirements.txt

:: Inicializar banco
echo 🗄️ Inicializando banco de dados...
python init_db.py

echo ✅ Setup completo!
echo.
echo 🚀 Para iniciar o servidor:
echo    .venv_clean\Scripts\activate.bat
echo    python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
echo.
echo 🧪 Para executar testes:
echo    python test_docker.py
pause