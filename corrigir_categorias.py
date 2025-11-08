"""
Script para corrigir valores de categoria no banco de dados
"""
import sqlite3
import sys
import os

# Conectar ao banco de dados
db_path = "galera_volei.db"

if not os.path.exists(db_path):
    print("❌ Banco de dados não encontrado!")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar valores atuais
    cursor.execute("SELECT DISTINCT categoria FROM partidas WHERE categoria IS NOT NULL")
    categorias_existentes = cursor.fetchall()
    print("📊 Categorias existentes no banco:")
    for cat in categorias_existentes:
        print(f"  - {cat[0]}")
    
    # Mapear valores incorretos para corretos
    mapeamento = {
        "livre": "livre",
        "LIVRE": "livre",
        "noob": "noob", 
        "NOOB": "noob",
        "amador": "amador",
        "AMADOR": "amador",
        "intermediario": "intermediario",
        "INTERMEDIARIO": "intermediario",
        "avancado": "avancado",
        "AVANCADO": "avancado"
    }
    
    # Atualizar valores se necessário
    for valor_antigo, valor_novo in mapeamento.items():
        cursor.execute(
            "UPDATE partidas SET categoria = ? WHERE categoria = ?",
            (valor_novo, valor_antigo)
        )
        if cursor.rowcount > 0:
            print(f"✅ Atualizados {cursor.rowcount} registros: '{valor_antigo}' -> '{valor_novo}'")
    
    # Definir categoria padrão para partidas sem categoria
    cursor.execute("UPDATE partidas SET categoria = 'livre' WHERE categoria IS NULL")
    if cursor.rowcount > 0:
        print(f"✅ Definida categoria 'livre' para {cursor.rowcount} partidas sem categoria")
    
    # Commit das mudanças
    conn.commit()
    
    # Verificar resultado final
    cursor.execute("SELECT DISTINCT categoria FROM partidas")
    categorias_finais = cursor.fetchall()
    print("\n📊 Categorias após correção:")
    for cat in categorias_finais:
        print(f"  - {cat[0]}")
    
    print("\n✅ Correção de categorias concluída com sucesso!")
    
except Exception as e:
    print(f"❌ Erro durante correção: {e}")
    conn.rollback()
finally:
    conn.close()