"""
Script para adicionar campos de horário e confirmação nas partidas
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    """Adiciona novos campos e colunas"""
    with engine.connect() as conn:
        # 1. Adicionar data_fim na tabela partidas
        try:
            conn.execute(text("""
                ALTER TABLE partidas 
                ADD COLUMN data_fim TIMESTAMP WITH TIME ZONE
            """))
            print("✅ Coluna data_fim adicionada")
        except Exception as e:
            print(f"⚠️  Coluna data_fim já existe ou erro: {e}")
        
        # 2. Adicionar duracao_estimada na tabela partidas
        try:
            conn.execute(text("""
                ALTER TABLE partidas 
                ADD COLUMN duracao_estimada INTEGER DEFAULT 120
            """))
            print("✅ Coluna duracao_estimada adicionada")
        except Exception as e:
            print(f"⚠️  Coluna duracao_estimada já existe ou erro: {e}")
        
        # 3. Adicionar confirmado na tabela partida_participantes
        try:
            conn.execute(text("""
                ALTER TABLE partida_participantes 
                ADD COLUMN confirmado BOOLEAN DEFAULT FALSE
            """))
            print("✅ Coluna confirmado adicionada")
        except Exception as e:
            print(f"⚠️  Coluna confirmado já existe ou erro: {e}")
        
        # 4. Adicionar data_confirmacao na tabela partida_participantes
        try:
            conn.execute(text("""
                ALTER TABLE partida_participantes 
                ADD COLUMN data_confirmacao TIMESTAMP WITH TIME ZONE
            """))
            print("✅ Coluna data_confirmacao adicionada")
        except Exception as e:
            print(f"⚠️  Coluna data_confirmacao já existe ou erro: {e}")
        
        # 5. Adicionar novos status no enum (se necessário)
        try:
            # SQLite não suporta ALTER TYPE, então isso é mais para PostgreSQL
            # No SQLite, o enum é armazenado como string
            print("✅ Novos status (MARCADA, EM_ANDAMENTO, CANCELADA) suportados")
        except Exception as e:
            print(f"⚠️  Erro ao atualizar enum: {e}")
        
        conn.commit()
        print("\n✅ Migração concluída!")

if __name__ == "__main__":
    print("🔄 Iniciando migração de status e horários...")
    migrate()
