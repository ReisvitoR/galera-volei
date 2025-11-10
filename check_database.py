"""
Script para verificar o banco de dados PostgreSQL
"""
from sqlalchemy import text, inspect
from app.core.database import engine, SessionLocal
from app.models.models import Usuario, Partida, Equipe, Candidatura, Avaliacao, Convite

def check_database():
    """Verifica se o banco está funcionando e mostra informações"""
    print("🔍 Verificando banco de dados PostgreSQL...\n")
    
    try:
        # 1. Testar conexão
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ Conexão estabelecida com sucesso!")
            print(f"📊 Versão do PostgreSQL: {version[:50]}...\n")
        
        # 2. Listar tabelas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tabelas encontradas ({len(tables)}):")
        for table in sorted(tables):
            print(f"  ✓ {table}")
        print()
        
        # 3. Verificar estrutura de cada tabela
        db = SessionLocal()
        try:
            # Contar registros em cada tabela
            print("📊 Quantidade de registros:")
            
            usuarios_count = db.query(Usuario).count()
            print(f"  👥 Usuários: {usuarios_count}")
            
            partidas_count = db.query(Partida).count()
            print(f"  🏐 Partidas: {partidas_count}")
            
            equipes_count = db.query(Equipe).count()
            print(f"  👕 Equipes: {equipes_count}")
            
            candidaturas_count = db.query(Candidatura).count()
            print(f"  📝 Candidaturas: {candidaturas_count}")
            
            avaliacoes_count = db.query(Avaliacao).count()
            print(f"  ⭐ Avaliações: {avaliacoes_count}")
            
            convites_count = db.query(Convite).count()
            print(f"  ✉️ Convites: {convites_count}")
            
            print()
            
            # 4. Verificar colunas de cada tabela
            print("🔧 Estrutura das tabelas principais:\n")
            
            for table_name in ['usuarios', 'partidas', 'equipes']:
                columns = inspector.get_columns(table_name)
                print(f"  📌 {table_name.upper()}:")
                for col in columns:
                    col_type = str(col['type'])
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"     - {col['name']}: {col_type} ({nullable})")
                print()
            
            # 5. Status final
            print("=" * 60)
            print("✅ BANCO DE DADOS FUNCIONANDO PERFEITAMENTE!")
            print("=" * 60)
            print("\n💡 O que você pode fazer agora:")
            print("  1. Registrar novos usuários")
            print("  2. Criar partidas")
            print("  3. Entrar em partidas")
            print("  4. Criar equipes")
            print("  5. Enviar convites")
            print("\n🎯 Todos os dados serão persistentes e não serão perdidos!")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        print("\n💡 Dica: Verifique se:")
        print("  1. O arquivo .env tem a URL correta do PostgreSQL")
        print("  2. O banco Koyeb está ativo")
        print("  3. As credenciais estão corretas")
        raise

if __name__ == "__main__":
    check_database()
