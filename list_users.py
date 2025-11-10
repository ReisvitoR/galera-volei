"""
Script para listar usuários do banco de dados
"""
from sqlalchemy import text
from app.core.database import engine

def list_users():
    """Lista todos os usuários do banco"""
    print("👥 Listando usuários do banco de dados...\n")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT id, nome, email, tipo, ativo, pontuacao_total, 
                       partidas_jogadas, vitorias, derrotas, created_at
                FROM usuarios
                ORDER BY id
            """))
            
            usuarios = result.fetchall()
            
            if not usuarios:
                print("❌ Nenhum usuário encontrado no banco")
                return
            
            print(f"📊 Total: {len(usuarios)} usuário(s)\n")
            print("=" * 100)
            
            for user in usuarios:
                print(f"\n🆔 ID: {user[0]}")
                print(f"👤 Nome: {user[1]}")
                print(f"📧 Email: {user[2]}")
                print(f"🎯 Tipo: {user[3]}")
                print(f"✅ Ativo: {'Sim' if user[4] else 'Não'}")
                print(f"⭐ Pontuação: {user[5]}")
                print(f"🏐 Partidas: {user[6]} | Vitórias: {user[7]} | Derrotas: {user[8]}")
                print(f"📅 Criado em: {user[9]}")
                print("-" * 100)
            
            print("\n✅ Listagem concluída!")
            
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        raise

if __name__ == "__main__":
    list_users()
