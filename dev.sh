#!/usr/bin/env bash
# Script de desenvolvimento usando uv

# Sincronizar dependências
echo "📦 Sincronizando dependências com uv..."
uv pip sync requirements.txt

# Inicializar banco de dados
echo "🗄️ Inicializando banco de dados..."
.venv/bin/python init_db.py

# Iniciar servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento..."
.venv/bin/uvicorn api:app --reload --host 0.0.0.0 --port 8000