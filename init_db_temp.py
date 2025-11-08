"""
Script temporário para inicializar o banco de dados com senhas compatíveis
"""
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models import Usuario
from app.models.enums import TipoUsuario
from app.core.security import Security

def init_db_temp():
    """Inicializar banco de dados com senhas truncadas"""
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Verificar se já existem usuários
        existing_user = db.query(Usuario).first()
        if existing_user:
            print("Banco já inicializado!")
            return
        
        # Criar usuário admin padrão (senha truncada se necessário)
        admin_password = "admin123"
        if len(admin_password.encode('utf-8')) > 72:
            admin_password = admin_password[:72]
            
        admin_user = Usuario(
            nome="Administrador",
            email="admin@galeravolei.com",
            senha_hash=Security.get_password_hash(admin_password),
            tipo=TipoUsuario.PROPLAYER,
            ativo=True
        )
        db.add(admin_user)
        
        # Criar usuários de exemplo
        usuarios_exemplo = [
            Usuario(
                nome="João Silva",
                email="joao@exemplo.com",
                senha_hash=Security.get_password_hash("123456"),
                tipo=TipoUsuario.INTERMEDIARIO,
                ativo=True,
                partidas_jogadas=15,
                vitorias=10,
                derrotas=5,
                pontuacao_total=250
            ),
            Usuario(
                nome="Maria Santos",
                email="maria@exemplo.com", 
                senha_hash=Security.get_password_hash("654321"),
                tipo=TipoUsuario.AMADOR,
                ativo=True,
                partidas_jogadas=8,
                vitorias=3,
                derrotas=5,
                pontuacao_total=120
            ),
            Usuario(
                nome="Pedro Oliveira",
                email="pedro@exemplo.com",
                senha_hash=Security.get_password_hash("senha123"),
                tipo=TipoUsuario.PROPLAYER,
                ativo=True,
                partidas_jogadas=25,
                vitorias=20,
                derrotas=5,
                pontuacao_total=500
            )
        ]
        
        for usuario in usuarios_exemplo:
            db.add(usuario)
        
        # Commit das mudanças
        db.commit()
        
        print("🏐 Banco de dados inicializado com sucesso!")
        print("👤 Usuários criados:")
        print("   Admin: admin@galeravolei.com / admin123")
        print("   João: joao@exemplo.com / 123456")
        print("   Maria: maria@exemplo.com / 654321")
        print("   Pedro: pedro@exemplo.com / senha123")
        
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db_temp()