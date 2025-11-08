"""
Script para migrar a tabela partida_participantes adicionando os novos campos
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    """Adiciona colunas à tabela partida_participantes"""
    with engine.connect() as conn:
        try:
            # Tentar adicionar a coluna convidado_por_id
            conn.execute(text("""
                ALTER TABLE partida_participantes 
                ADD COLUMN convidado_por_id INTEGER REFERENCES usuarios(id)
            """))
            print("✅ Coluna convidado_por_id adicionada")
        except Exception as e:
            print(f"⚠️  Coluna convidado_por_id já existe ou erro: {e}")
        
        try:
            # Tentar adicionar a coluna data_entrada
            conn.execute(text("""
                ALTER TABLE partida_participantes 
                ADD COLUMN data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            print("✅ Coluna data_entrada adicionada")
        except Exception as e:
            print(f"⚠️  Coluna data_entrada já existe ou erro: {e}")
        
        conn.commit()
        print("\n✅ Migração concluída!")

if __name__ == "__main__":
    print("🔄 Iniciando migração da tabela partida_participantes...")
    migrate()
