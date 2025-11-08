from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.models import Convite
from app.models.enums import StatusConvite
from app.schemas.schemas import ConviteCreate, ConviteUpdate


class ConviteRepository(BaseRepository[Convite]):
    def __init__(self, db: Session):
        super().__init__(db, Convite)
    
    def get(self, id: int) -> Optional[Convite]:
        """Buscar convite por ID incluindo relacionamentos"""
        return (
            self.db.query(Convite)
            .options(
                joinedload(Convite.mandante),
                joinedload(Convite.convidado),
                joinedload(Convite.partida)
            )
            .filter(Convite.id == id)
            .first()
        )
    
    def create(self, obj_in: dict) -> Convite:
        """Criar convite incluindo relacionamentos"""
        print(f"DEBUG CONVITE REPO: Chamando super().create com: {obj_in}")
        print(f"DEBUG CONVITE REPO: Tipo obj_in: {type(obj_in)}")
        
        convite = super().create(obj_in)
        print(f"DEBUG CONVITE REPO: Convite criado no super: {convite}")
        print(f"DEBUG CONVITE REPO: ID do convite: {convite.id}")
        
        # Retornar diretamente o convite criado (sem recarregar)
        return convite
    
    def get_convites_enviados(self, mandante_id: int, skip: int = 0, limit: int = 100) -> List[Convite]:
        """Buscar convites enviados por um usuário"""
        return (
            self.db.query(Convite)
            .filter(Convite.mandante_id == mandante_id)
            .order_by(Convite.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_convites_recebidos(self, convidado_id: int, skip: int = 0, limit: int = 100) -> List[Convite]:
        """Buscar convites recebidos por um usuário"""
        return (
            self.db.query(Convite)
            .filter(Convite.convidado_id == convidado_id)
            .order_by(Convite.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_convites_pendentes(self, convidado_id: int) -> List[Convite]:
        """Buscar convites pendentes de um usuário"""
        return (
            self.db.query(Convite)
            .filter(
                and_(
                    Convite.convidado_id == convidado_id,
                    Convite.status == StatusConvite.PENDENTE
                )
            )
            .order_by(Convite.created_at.desc())
            .all()
        )
    
    def get_convites_da_partida(self, partida_id: int) -> List[Convite]:
        """Buscar todos os convites de uma partida específica"""
        return (
            self.db.query(Convite)
            .filter(Convite.partida_id == partida_id)
            .order_by(Convite.created_at.desc())
            .all()
        )
    
    def convite_existe(self, mandante_id: int, convidado_id: int, partida_id: int) -> bool:
        """Verificar se já existe um convite ativo entre os usuários para a partida"""
        convite = (
            self.db.query(Convite)
            .filter(
                and_(
                    Convite.mandante_id == mandante_id,
                    Convite.convidado_id == convidado_id,
                    Convite.partida_id == partida_id,
                    Convite.status.in_([StatusConvite.PENDENTE, StatusConvite.ACEITO])
                )
            )
            .first()
        )
        return convite is not None
    
    def aceitar_convite(self, convite_id: int, convidado_id: int) -> Optional[Convite]:
        """Aceitar um convite específico"""
        convite = (
            self.db.query(Convite)
            .filter(
                and_(
                    Convite.id == convite_id,
                    Convite.convidado_id == convidado_id,
                    Convite.status == StatusConvite.PENDENTE
                )
            )
            .first()
        )
        
        if convite:
            convite.status = StatusConvite.ACEITO
            convite.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(convite)
        
        return convite
    
    def recusar_convite(self, convite_id: int, convidado_id: int) -> Optional[Convite]:
        """Recusar um convite específico"""
        convite = (
            self.db.query(Convite)
            .filter(
                and_(
                    Convite.id == convite_id,
                    Convite.convidado_id == convidado_id,
                    Convite.status == StatusConvite.PENDENTE
                )
            )
            .first()
        )
        
        if convite:
            convite.status = StatusConvite.RECUSADO
            convite.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(convite)
        
        return convite
    
    def expirar_convites_antigos(self) -> int:
        """Marcar como expirados os convites que passaram da data de expiração"""
        now = datetime.utcnow()
        count = (
            self.db.query(Convite)
            .filter(
                and_(
                    Convite.status == StatusConvite.PENDENTE,
                    Convite.data_expiracao.isnot(None),
                    Convite.data_expiracao < now
                )
            )
            .update(
                {
                    "status": StatusConvite.EXPIRADO,
                    "updated_at": now
                }
            )
        )
        self.db.commit()
        return count