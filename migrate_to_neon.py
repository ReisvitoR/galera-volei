"""
Script para criar tabelas no PostgreSQL do Neon.tech
"""
from app.core.database import engine, Base
from app.models.models import Usuario, Partida, Equipe, Candidatura, Avaliacao, Convite  # noqa: F401

def migrate_to_neon():
    """Cria todas as tabelas no Neon PostgreSQL"""
    print("🔄 Criando tabelas no Neon PostgreSQL...\n")
    
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Todas as tabelas foram criadas com sucesso!\n")
        print("📋 Tabelas criadas:")
        print("  - usuarios")
        print("  - partidas")
        print("  - equipes")
        print("  - candidaturas")
        print("  - avaliacoes")
        print("  - convites")
        print("  - partida_participantes (associação)")
        print("  - equipe_membros (associação)")
        print("\n🎉 Banco de dados pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise

if __name__ == "__main__":
    migrate_to_neon()
