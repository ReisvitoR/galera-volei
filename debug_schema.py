"""
Teste isolado do schema ConviteCreate
"""
from app.schemas.schemas import ConviteCreate
from datetime import datetime, timedelta

def test_convite_create_schema():
    """Testar se o schema ConviteCreate está funcionando"""
    
    try:
        print("Testando criação do schema ConviteCreate...")
        
        convite_data = {
            "convidado_id": 1,
            "partida_id": 1,
            "mensagem": "Teste schema"
        }
        
        print(f"Dados de entrada: {convite_data}")
        
        convite = ConviteCreate(**convite_data)
        print(f"✅ Schema criado com sucesso: {convite}")
        print(f"Campos: convidado_id={convite.convidado_id}, partida_id={convite.partida_id}, mensagem={convite.mensagem}")
        
        # Testar serialização JSON
        json_data = convite.model_dump()
        print(f"JSON serializado: {json_data}")
        
        # Testar deserialização
        convite_from_json = ConviteCreate.model_validate(json_data)
        print(f"✅ Deserialização funcionou: {convite_from_json}")
        
    except Exception as e:
        print(f"❌ Erro no schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_convite_create_schema()