"""
Script para atualizar tipos de enum no banco de dados PostgreSQL
"""
from sqlalchemy import text
from app.core.database import engine

def update_enum_types():
    """Atualiza os tipos de enum no banco de dados"""
    print("🔄 Atualizando tipos de enum no PostgreSQL...\n")
    
    with engine.connect() as connection:
        # Iniciar transação
        trans = connection.begin()
        
        try:
            # 1. Atualizar TipoUsuario
            print("📝 Atualizando tipo_usuario...")
            connection.execute(text("""
                UPDATE usuarios
                SET tipo = CASE tipo
                    WHEN 'noob' THEN 'iniciante'
                    WHEN 'amador' THEN 'intermediario'
                    WHEN 'intermediario' THEN 'intermediario'
                    WHEN 'proplayer' THEN 'profissional'
                    ELSE tipo
                END
            """))
            print("  ✓ TipoUsuario atualizado")
            
            # 2. Atualizar TipoPartida
            print("📝 Atualizando tipo_partida...")
            connection.execute(text("""
                UPDATE partidas
                SET tipo = CASE tipo
                    WHEN 'iniciante' THEN 'amistosa'
                    WHEN 'normal' THEN 'amistosa'
                    WHEN 'ranked' THEN 'competitiva'
                    ELSE tipo
                END
            """))
            print("  ✓ TipoPartida atualizado")
            
            # 3. Atualizar CategoriaPartida
            print("📝 Atualizando categoria_partida...")
            connection.execute(text("""
                UPDATE partidas
                SET categoria = CASE categoria
                    WHEN 'noob' THEN 'iniciante'
                    WHEN 'amador' THEN 'intermediario'
                    WHEN 'intermediario' THEN 'intermediario'
                    WHEN 'avancado' THEN 'avancado'
                    WHEN 'livre' THEN 'livre'
                    ELSE categoria
                END
            """))
            print("  ✓ CategoriaPartida atualizado")
            
            # Confirmar transação
            trans.commit()
            
            print("\n✅ Todos os tipos foram atualizados com sucesso!")
            print("\n📊 Novos valores:")
            print("  TipoUsuario: iniciante, intermediario, avancado, profissional")
            print("  TipoPartida: amistosa, competitiva")
            print("  CategoriaPartida: iniciante, intermediario, avancado, profissional, livre")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Erro ao atualizar tipos: {e}")
            raise

if __name__ == "__main__":
    update_enum_types()
