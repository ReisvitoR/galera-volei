"""
Teste isolado do ConviteRepository
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.repositories.convite_repository import ConviteRepository
from app.models.enums import StatusConvite
from datetime import datetime, timedelta

def test_convite_repository():
    """Testar se o ConviteRepository está funcionando"""
    
    db = SessionLocal()
    
    try:
        print("Testando criação do ConviteRepository...")
        
        repo = ConviteRepository(db)
        print(f"✅ Repository criado: {repo}")
        
        # Testar criação
        convite_data = {
            "mensagem": "Teste repository",
            "data_expiracao": datetime.now() + timedelta(days=7),
            "mandante_id": 1,
            "convidado_id": 2,
            "partida_id": 1,
            "status": StatusConvite.PENDENTE
        }
        
        print(f"Dados para criar: {convite_data}")
        
        convite = repo.create(convite_data)
        print(f"✅ Convite criado via repository: {convite}")
        print(f"ID: {convite.id}, Status: {convite.status}")
        
    except Exception as e:
        print(f"❌ Erro no repository: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_convite_repository()