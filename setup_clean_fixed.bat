@echo off
set PYTHON_EXE="C:\Users\Nazir Reis\AppData\Local\Programs\Python\Python311\python.exe"

echo 🐍 SETUP AMBIENTE LIMPO - GALERA VOLEI API
echo ============================================

:: Limpar ambiente anterior
if exist ".venv_clean" (
    echo 🧹 Removendo ambiente anterior...
    rmdir /s /q ".venv_clean"
)

:: Criar novo ambiente virtual
echo 🔧 Criando ambiente virtual limpo...
%PYTHON_EXE% -m venv .venv_clean

:: Ativar ambiente
echo 🔄 Ativando ambiente...
call .venv_clean\Scripts\activate.bat

:: Atualizar pip
echo 📦 Atualizando pip...
%PYTHON_EXE% -m pip install --upgrade pip

:: Instalar dependências
echo 📋 Instalando dependências...
.venv_clean\Scripts\pip.exe install -r requirements.txt

:: Inicializar banco
echo 🗄️ Inicializando banco de dados...
.venv_clean\Scripts\python.exe init_db.py

echo.
echo ✅ Setup completo!
echo.
echo 🚀 Para iniciar o servidor execute:
echo    start_server.bat
echo.
echo 🧪 Para executar testes execute:
echo    test_clean.bat
pause