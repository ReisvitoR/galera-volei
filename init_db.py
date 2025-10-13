"""
Script para inicializar o banco de dados e criar dados de exemplo
"""
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models import Usuario
from app.models.enums import TipoUsuario
from app.core.security import security


def init_db():
    """Inicializar banco de dados"""
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
        
        # Criar usuário admin padrão
        admin_user = Usuario(
            nome="Administrador",
            email="admin@galeravolei.com",
            senha_hash=security.get_password_hash("admin123"),
            tipo=TipoUsuario.PROPLAYER,
            ativo=True
        )
        db.add(admin_user)
        
        # Criar usuários de exemplo
        usuarios_exemplo = [
            Usuario(
                nome="João Silva",
                email="joao@exemplo.com",
                senha_hash=security.get_password_hash("123456"),
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
                senha_hash=security.get_password_hash("123456"),
                tipo=TipoUsuario.AMADOR,
                ativo=True,
                partidas_jogadas=8,
                vitorias=5,
                derrotas=3,
                pontuacao_total=120
            ),
            Usuario(
                nome="Pedro Costa",
                email="pedro@exemplo.com",
                senha_hash=security.get_password_hash("123456"),
                tipo=TipoUsuario.NOOB,
                ativo=True,
                partidas_jogadas=3,
                vitorias=1,
                derrotas=2,
                pontuacao_total=35
            )
        ]
        
        for usuario in usuarios_exemplo:
            db.add(usuario)
        
        # Salvar no banco
        db.commit()
        
        print("Banco de dados inicializado com sucesso!")
        print("Usuário admin criado:")
        print("  Email: admin@galeravolei.com")
        print("  Senha: admin123")
        print()
        print("Usuários de exemplo criados:")
        for usuario in usuarios_exemplo:
            print(f"  {usuario.nome} ({usuario.email}) - Tipo: {usuario.tipo.value}")
        
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()