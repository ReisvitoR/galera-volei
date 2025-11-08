from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from app.models import Partida, Usuario
from app.models.enums import StatusPartida, TipoPartida, CategoriaPartida
from app.repositories.base import BaseRepository


class PartidaRepository(BaseRepository[Partida]):
    """Repository para operações com partidas"""
    
    def __init__(self, db: Session):
        super().__init__(db, Partida)
    
    def get_with_details(self, partida_id: int) -> Optional[Partida]:
        """Buscar partida com organizador e participantes"""
        return (
            self.db.query(Partida)
            .options(
                joinedload(Partida.organizador),
                joinedload(Partida.participantes)
            )
            .filter(Partida.id == partida_id)
            .first()
        )
    
    def get_by_status(self, status: StatusPartida, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Buscar partidas por status"""
        return (
            self.db.query(Partida)
            .options(joinedload(Partida.organizador))
            .filter(Partida.status == status)
            .order_by(desc(Partida.data_partida))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_tipo(self, tipo: TipoPartida, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Buscar partidas por tipo"""
        return (
            self.db.query(Partida)
            .options(joinedload(Partida.organizador))
            .filter(Partida.tipo == tipo)
            .filter(Partida.status == StatusPartida.ATIVA)
            .order_by(Partida.data_partida)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_categoria(self, categoria: str, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Buscar partidas por categoria"""
        return (
            self.db.query(Partida)
            .options(joinedload(Partida.organizador))
            .filter(Partida.categoria == categoria)
            .filter(Partida.status == StatusPartida.ATIVA)
            .order_by(Partida.data_partida)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_organizador(self, organizador_id: int, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Buscar partidas por organizador"""
        return (
            self.db.query(Partida)
            .options(joinedload(Partida.participantes))
            .filter(Partida.organizador_id == organizador_id)
            .order_by(desc(Partida.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_participando(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Buscar partidas onde usuário está participando"""
        return (
            self.db.query(Partida)
            .join(Partida.participantes)
            .options(joinedload(Partida.organizador))
            .filter(Usuario.id == usuario_id)
            .order_by(desc(Partida.data_partida))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_proximas(self, limite_data: datetime, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Buscar próximas partidas ativas"""
        return (
            self.db.query(Partida)
            .options(joinedload(Partida.organizador))
            .filter(Partida.status == StatusPartida.ATIVA)
            .filter(Partida.data_partida >= limite_data)
            .order_by(Partida.data_partida)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def adicionar_participante(self, partida_id: int, usuario_id: int) -> bool:
        """Adicionar participante à partida"""
        partida = self.get_with_details(partida_id)
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if partida and usuario and len(partida.participantes) < partida.max_participantes:
            partida.participantes.append(usuario)
            self.db.commit()
            return True
        return False
    
    def remover_participante(self, partida_id: int, usuario_id: int) -> bool:
        """Remover participante da partida"""
        partida = self.get_with_details(partida_id)
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if partida and usuario and usuario in partida.participantes:
            partida.participantes.remove(usuario)
            self.db.commit()
            return True
        return False
    
    def atualizar_pontuacao(self, partida_id: int, pontos_a: int, pontos_b: int) -> bool:
        """Atualizar pontuação da partida"""
        partida = self.get(partida_id)
        if partida:
            partida.pontuacao_equipe_a = pontos_a
            partida.pontuacao_equipe_b = pontos_b
            if pontos_a != pontos_b:  # Partida finalizada
                partida.status = StatusPartida.FINALIZADA
            self.db.commit()
            self.db.refresh(partida)
            return True
        return False