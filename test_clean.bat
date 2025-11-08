@echo off
echo 🧪 Executando testes no ambiente limpo...
call .venv_clean\Scripts\activate.bat
.venv_clean\Scripts\python.exe test_docker.py
pause