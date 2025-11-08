"""
Script para inicializar o banco de dados na primeira execução
"""
import os
from app.core.database import engine, Base, SessionLocal
from app.models.models import Usuario, Partida
from app.models.enums import TipoUsuario
from app.core.security import get_password_hash

def init_db():
    """Inicializar banco de dados"""
    print("🔄 Criando tabelas do banco de dados...")
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tabelas criadas com sucesso!")
    
    # Verificar se já existe usuário administrador
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.email == "admin@galeravolei.com").first()
        
        if not admin:
            print("🔄 Criando usuário administrador...")
            admin = Usuario(
                nome="Administrador",
                email="admin@galeravolei.com",
                senha_hash=get_password_hash("admin123"),
                tipo=TipoUsuario.PROPLAYER,
                ativo=True
            )
            db.add(admin)
            db.commit()
            print("✅ Usuário administrador criado!")
            print("   Email: admin@galeravolei.com")
            print("   Senha: admin123")
        else:
            print("✅ Usuário administrador já existe")
            
    except Exception as e:
        print(f"⚠️ Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("🎉 Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_db()