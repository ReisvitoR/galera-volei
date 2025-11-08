"""
Debug do problema de criação de convite
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Convite
from app.models.enums import StatusConvite
from datetime import datetime, timedelta

def test_convite_creation():
    """Testar criação direta de convite"""
    db = SessionLocal()
    
    try:
        # Criar convite diretamente
        convite_data = {
            "mensagem": "Teste direto",
            "data_expiracao": datetime.now() + timedelta(days=7),
            "mandante_id": 1,
            "convidado_id": 2,
            "partida_id": 1,
            "status": StatusConvite.PENDENTE
        }
        
        print(f"Dados para criar: {convite_data}")
        print(f"Tipo do status: {type(convite_data['status'])}")
        
        # Criar usando SQLAlchemy diretamente
        convite = Convite(**convite_data)
        print(f"Convite criado: {convite}")
        
        db.add(convite)
        db.commit()
        db.refresh(convite)
        
        print(f"✅ Convite salvo com ID: {convite.id}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_convite_creation()