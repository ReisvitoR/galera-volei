"""
Teste isolado do repository para debug
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import DATABASE_URL
from app.models.models import Convite
from app.models.enums import StatusConvite
from app.repositories.convite_repository import ConviteRepository

def test_repository_direto():
    """Teste direto do repository"""
    print("=== Teste Repository Direto ===")
    
    # Conectar ao banco
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Criar repository
        convite_repo = ConviteRepository(db)
        print("Repository criado com sucesso")
        
        # Dados do convite
        convite_data = {
            "mensagem": "Teste repository direto",
            "data_expiracao": datetime.now() + timedelta(days=7),
            "mandante_id": 39,  # ID do nosso usuário de teste
            "convidado_id": 1,
            "partida_id": 14,
            "status": StatusConvite.PENDENTE
        }
        
        print(f"Dados do convite: {convite_data}")
        print(f"Tipo dos dados: {type(convite_data)}")
        
        # Tentar criar o convite
        convite_criado = convite_repo.create(convite_data)
        print(f"✅ Convite criado com sucesso!")
        print(f"ID: {convite_criado.id}")
        print(f"Mensagem: {convite_criado.mensagem}")
        print(f"Status: {convite_criado.status}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_repository_direto()