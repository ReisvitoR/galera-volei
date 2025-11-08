@echo off
REM Script de desenvolvimento para Windows usando uv

echo 📦 Sincronizando dependências com uv...
uv pip sync requirements.txt

echo 🗄️ Inicializando banco de dados...
.venv\Scripts\python.exe init_db.py

echo 🚀 Iniciando servidor de desenvolvimento...
.venv\Scripts\uvicorn.exe api:app --reload --host 0.0.0.0 --port 8000