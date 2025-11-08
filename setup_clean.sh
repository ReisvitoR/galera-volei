#!/bin/bash
echo "🐍 SETUP AMBIENTE LIMPO - GALERA VOLEI API"
echo "============================================"

# Limpar ambiente anterior
if [ -d ".venv_clean" ]; then
    echo "🧹 Removendo ambiente anterior..."
    rm -rf .venv_clean
fi

# Criar novo ambiente virtual
echo "🔧 Criando ambiente virtual limpo..."
python3 -m venv .venv_clean

# Ativar ambiente
echo "🔄 Ativando ambiente..."
source .venv_clean/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Instalar dependências
echo "📋 Instalando dependências..."
pip install -r requirements.txt

# Inicializar banco
echo "🗄️ Inicializando banco de dados..."
python init_db.py

echo "✅ Setup completo!"
echo ""
echo "🚀 Para iniciar o servidor:"
echo "   source .venv_clean/bin/activate"
echo "   python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "🧪 Para executar testes:"
echo "   python test_docker.py"