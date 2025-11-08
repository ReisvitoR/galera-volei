"""
Utilitário para gerenciar status automático das partidas
"""
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from app.models.models import Partida, partida_participantes
from app.models.enums import StatusPartida


def get_horario_brasil() -> datetime:
    """Retorna o horário atual no timezone do Brasil"""
    tz_brasil = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz_brasil)


def atualizar_status_partida(partida: Partida, db: Session) -> bool:
    """
    Atualiza automaticamente o status da partida baseado em:
    - Horário atual
    - Confirmações dos participantes
    - Data de início e fim
    
    Retorna True se o status foi alterado
    """
    agora = get_horario_brasil()
    status_anterior = partida.status
    
    # Se já está finalizada ou cancelada, não muda
    if partida.status in [StatusPartida.FINALIZADA, StatusPartida.CANCELADA]:
        return False
    
    # Calcular horário de fim baseado na duração
    if partida.data_fim:
        horario_fim = partida.data_fim
    else:
        horario_fim = partida.data_partida + timedelta(minutes=partida.duracao_estimada)
    
    # Tornar datas aware se necessário
    if partida.data_partida.tzinfo is None:
        tz_brasil = pytz.timezone('America/Sao_Paulo')
        data_partida = tz_brasil.localize(partida.data_partida)
        horario_fim = tz_brasil.localize(horario_fim) if horario_fim.tzinfo is None else horario_fim
    else:
        data_partida = partida.data_partida
    
    # 1. Se passou do horário de fim -> FINALIZADA
    if agora > horario_fim:
        partida.status = StatusPartida.FINALIZADA
        db.commit()
        return True
    
    # 2. Se está no horário (início <= agora < fim) -> EM_ANDAMENTO
    if data_partida <= agora < horario_fim:
        if partida.status != StatusPartida.EM_ANDAMENTO:
            partida.status = StatusPartida.EM_ANDAMENTO
            db.commit()
            return True
        return False
    
    # 3. Se ainda não chegou o horário, verificar confirmações
    if agora < data_partida:
        # Contar confirmações
        stmt = select(partida_participantes).where(
            and_(
                partida_participantes.c.partida_id == partida.id,
                partida_participantes.c.confirmado == True
            )
        )
        result = db.execute(stmt)
        confirmados = len(result.fetchall())
        total_participantes = len(partida.participantes)
        
        # Se todos confirmaram e tem pelo menos 1 participante -> MARCADA
        if total_participantes > 0 and confirmados == total_participantes:
            if partida.status != StatusPartida.MARCADA:
                partida.status = StatusPartida.MARCADA
                db.commit()
                return True
        # Se não está marcada e tinha ficado marcada antes, volta para ATIVA
        elif partida.status == StatusPartida.MARCADA:
            partida.status = StatusPartida.ATIVA
            db.commit()
            return True
    
    return status_anterior != partida.status


def verificar_confirmacoes(partida: Partida, db: Session) -> dict:
    """
    Retorna informações sobre as confirmações da partida
    """
    stmt = select(partida_participantes).where(
        partida_participantes.c.partida_id == partida.id
    )
    result = db.execute(stmt)
    rows = result.fetchall()
    
    total = len(rows)
    confirmados = sum(1 for row in rows if row.confirmado)
    
    return {
        "total_participantes": total,
        "participantes_confirmados": confirmados,
        "todos_confirmaram": total > 0 and confirmados == total,
        "percentual_confirmacao": (confirmados / total * 100) if total > 0 else 0
    }


def confirmar_presenca(partida_id: int, usuario_id: int, db: Session) -> bool:
    """
    Confirma a presença de um participante na partida
    Retorna True se conseguiu confirmar
    """
    agora = get_horario_brasil()
    
    stmt = (
        update(partida_participantes)
        .where(
            and_(
                partida_participantes.c.partida_id == partida_id,
                partida_participantes.c.usuario_id == usuario_id
            )
        )
        .values(confirmado=True, data_confirmacao=agora)
    )
    
    result = db.execute(stmt)
    db.commit()
    
    return result.rowcount > 0


def cancelar_confirmacao(partida_id: int, usuario_id: int, db: Session) -> bool:
    """
    Cancela a confirmação de presença de um participante
    Retorna True se conseguiu cancelar
    """
    stmt = (
        update(partida_participantes)
        .where(
            and_(
                partida_participantes.c.partida_id == partida_id,
                partida_participantes.c.usuario_id == usuario_id
            )
        )
        .values(confirmado=False, data_confirmacao=None)
    )
    
    result = db.execute(stmt)
    db.commit()
    
    return result.rowcount > 0
