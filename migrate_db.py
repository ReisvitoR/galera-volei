"""
Script para criar todas as tabelas no PostgreSQL
"""
from app.core.database import engine, Base
from app.models.models import Usuario, Partida, Equipe, Candidatura, Avaliacao, Convite

def migrate_to_postgres():
    """Cria todas as tabelas no PostgreSQL"""
    print("🔄 Iniciando migração para PostgreSQL...")
    
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Todas as tabelas foram criadas com sucesso no PostgreSQL!")
        print("\n📋 Tabelas criadas:")
        print("  - usuarios")
        print("  - partidas")
        print("  - equipes")
        print("  - candidaturas")
        print("  - avaliacoes")
        print("  - convites")
        print("  - partida_participantes (tabela de associação)")
        print("  - equipe_membros (tabela de associação)")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise

if __name__ == "__main__":
    migrate_to_postgres()
