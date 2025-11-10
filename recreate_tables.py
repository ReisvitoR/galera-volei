"""
Script para recriar as tabelas com os novos tipos de enum
"""
from app.core.database import engine, Base
from app.models.models import Usuario, Partida, Equipe, Candidatura, Avaliacao, Convite
from sqlalchemy import text

def recreate_tables():
    """Remove todas as tabelas e recria com os novos enums"""
    print("🔄 Recriando tabelas com novos tipos de enum...\n")
    
    print("⚠️  ATENÇÃO: Isso vai APAGAR TODOS OS DADOS!")
    print("📋 Tabelas que serão recriadas:")
    print("  - usuarios")
    print("  - partidas")
    print("  - equipes")
    print("  - candidaturas")
    print("  - avaliacoes")
    print("  - convites")
    print("  - partida_participantes")
    print("  - equipe_membros")
    print()
    
    confirmacao = input("Digite 'SIM' para confirmar: ")
    
    if confirmacao.upper() != "SIM":
        print("❌ Operação cancelada")
        return
    
    try:
        with engine.connect() as connection:
            print("\n🗑️  Removendo tabelas antigas...")
            
            # Remover tabelas em ordem reversa de dependência
            connection.execute(text("DROP TABLE IF EXISTS avaliacoes CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS candidaturas CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS convites CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS equipe_membros CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS partida_participantes CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS equipes CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS partidas CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS usuarios CASCADE"))
            
            # Remover tipos enum antigos
            connection.execute(text("DROP TYPE IF EXISTS tipousuario CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS tipopartida CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS categoriapartida CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS statuspartida CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS statuscandidatura CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS statusconvite CASCADE"))
            
            connection.commit()
            print("  ✓ Tabelas e tipos removidos")
        
        # Recriar tabelas
        print("\n📝 Criando novas tabelas...")
        Base.metadata.create_all(bind=engine)
        print("  ✓ Tabelas criadas")
        
        print("\n✅ Banco de dados recriado com sucesso!")
        print("\n📊 Novos tipos:")
        print("  TipoUsuario: iniciante, intermediario, avancado, profissional")
        print("  TipoPartida: amistosa, competitiva")
        print("  CategoriaPartida: iniciante, intermediario, avancado, profissional, livre")
        
    except Exception as e:
        print(f"\n❌ Erro ao recriar tabelas: {e}")
        raise

if __name__ == "__main__":
    recreate_tables()
