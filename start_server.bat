@echo off
echo 🚀 Iniciando servidor no ambiente limpo...
call .venv_clean\Scripts\activate.bat
.venv_clean\Scripts\python.exe -m uvicorn api:app --reload --host 127.0.0.1 --port 8000