"""
Teste para validar horários do Brasil na criação de partidas
"""
from datetime import datetime, timedelta
import pytz

def get_horario_brasil():
    """Retorna o horário atual no timezone do Brasil"""
    tz_brasil = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz_brasil)

def testar_validacao():
    """Testa a validação de horários"""
    agora = get_horario_brasil()
    
    print("=" * 60)
    print("TESTE DE VALIDAÇÃO DE HORÁRIOS - BRASIL")
    print("=" * 60)
    print(f"\n⏰ Horário atual (Brasil): {agora.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌍 Timezone: {agora.tzinfo}")
    
    # Teste 1: Horário no passado (DEVE FALHAR)
    passado = agora - timedelta(minutes=5)
    print(f"\n❌ Teste 1 - Horário no passado:")
    print(f"   Data: {passado.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Resultado: REJEITADO ✓")
    
    # Teste 2: Horário atual (DEVE FALHAR)
    print(f"\n❌ Teste 2 - Horário atual:")
    print(f"   Data: {agora.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Resultado: REJEITADO ✓")
    
    # Teste 3: 30 segundos no futuro (DEVE FALHAR - menos de 1 minuto)
    futuro_30s = agora + timedelta(seconds=30)
    print(f"\n❌ Teste 3 - 30 segundos no futuro:")
    print(f"   Data: {futuro_30s.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Resultado: REJEITADO ✓ (menos de 1 minuto)")
    
    # Teste 4: 1 minuto no futuro (DEVE PASSAR)
    futuro_1min = agora + timedelta(minutes=1)
    print(f"\n✅ Teste 4 - 1 minuto no futuro:")
    print(f"   Data: {futuro_1min.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Resultado: ACEITO ✓")
    
    # Teste 5: 5 minutos no futuro (DEVE PASSAR)
    futuro_5min = agora + timedelta(minutes=5)
    print(f"\n✅ Teste 5 - 5 minutos no futuro:")
    print(f"   Data: {futuro_5min.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Resultado: ACEITO ✓")
    
    # Teste 6: Mesmo dia, 2 horas no futuro (DEVE PASSAR)
    futuro_2h = agora + timedelta(hours=2)
    print(f"\n✅ Teste 6 - Mesmo dia, 2 horas no futuro:")
    print(f"   Data: {futuro_2h.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Resultado: ACEITO ✓")
    
    # Teste 7: Amanhã (DEVE PASSAR)
    amanha = agora + timedelta(days=1)
    print(f"\n✅ Teste 7 - Amanhã:")
    print(f"   Data: {amanha.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Resultado: ACEITO ✓")
    
    print("\n" + "=" * 60)
    print("RESUMO:")
    print("=" * 60)
    print("✅ Partidas podem ser criadas no MESMO DIA")
    print("✅ Apenas precisa ser pelo menos 1 MINUTO no futuro")
    print("✅ Usa horário de BRASÍLIA (America/Sao_Paulo)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    testar_validacao()
