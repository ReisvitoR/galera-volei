"""
Script para recriar tabelas do banco de dados com os novos campos
"""
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models import Usuario, Partida, Convite
from app.models.enums import TipoUsuario
from app.core.security import security
import os


def recreate_db():
    """Recriar banco de dados com estrutura atualizada"""
    print("🔄 Recriando tabelas do banco de dados...")
    
    # Remover arquivo do banco se existir
    db_file = "galera_volei.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Arquivo {db_file} removido")
    
    # Recriar todas as tabelas
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas recriadas com sucesso")
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Criar usuário admin padrão
        admin_user = Usuario(
            nome="Administrador",
            email="admin@galeravolei.com",
            senha_hash=security.get_password_hash("admin123"),
            tipo=TipoUsuario.PROPLAYER,  # Usar o nível mais alto disponível
            ativo=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Usuário admin criado com ID: {admin_user.id}")
        print("📧 Email: admin@galeravolei.com")
        print("🔑 Senha: admin123")
        
        # Criar usuário teste
        test_user = Usuario(
            nome="João Silva",
            email="joao@test.com",
            senha_hash=security.get_password_hash("senha123"),
            tipo=TipoUsuario.NOOB,
            ativo=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Usuário teste criado com ID: {test_user.id}")
        print("📧 Email: joao@test.com")
        print("🔑 Senha: senha123")
        
        print("\n🎉 Banco de dados recriado e inicializado com sucesso!")
        print("📝 Novos campos adicionados:")
        print("   - partidas.publica (Boolean)")
        print("   - Tabela convites completa")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    recreate_db()