from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models import Equipe, Usuario
from app.repositories.base import BaseRepository


class EquipeRepository(BaseRepository[Equipe]):
    """Repository para operações com equipes"""
    
    def __init__(self, db: Session):
        super().__init__(db, Equipe)
    
    def get_with_members(self, equipe_id: int) -> Equipe:
        """Buscar equipe com líder e membros"""
        return (
            self.db.query(Equipe)
            .options(
                joinedload(Equipe.lider),
                joinedload(Equipe.membros)
            )
            .filter(Equipe.id == equipe_id)
            .first()
        )
    
    def get_by_lider(self, lider_id: int) -> List[Equipe]:
        """Buscar equipes lideradas por um usuário"""
        return (
            self.db.query(Equipe)
            .options(joinedload(Equipe.membros))
            .filter(Equipe.lider_id == lider_id)
            .order_by(desc(Equipe.created_at))
            .all()
        )
    
    def get_ranking(self, limit: int = 10) -> List[Equipe]:
        """Buscar ranking de equipes por pontuação"""
        return (
            self.db.query(Equipe)
            .options(joinedload(Equipe.lider))
            .order_by(desc(Equipe.pontuacao_total))
            .limit(limit)
            .all()
        )
    
    def get_melhores_equipes(self, limit: int = 10) -> List[Equipe]:
        """Buscar melhores equipes por taxa de vitória"""
        return (
            self.db.query(Equipe)
            .options(joinedload(Equipe.lider))
            .filter(Equipe.partidas_jogadas > 0)
            .order_by(desc(Equipe.vitorias / Equipe.partidas_jogadas))
            .limit(limit)
            .all()
        )
    
    def adicionar_membro(self, equipe_id: int, usuario_id: int) -> bool:
        """Adicionar membro à equipe"""
        equipe = self.get_with_members(equipe_id)
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if equipe and usuario and usuario not in equipe.membros:
            equipe.membros.append(usuario)
            self.db.commit()
            return True
        return False
    
    def remover_membro(self, equipe_id: int, usuario_id: int) -> bool:
        """Remover membro da equipe"""
        equipe = self.get_with_members(equipe_id)
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if equipe and usuario and usuario in equipe.membros:
            equipe.membros.remove(usuario)
            self.db.commit()
            return True
        return False
    
    def update_stats(self, equipe_id: int, partidas_jogadas: int = 1, vitorias: int = 0, pontos: int = 0):
        """Atualizar estatísticas da equipe"""
        equipe = self.get(equipe_id)
        if equipe:
            equipe.partidas_jogadas += partidas_jogadas
            equipe.vitorias += vitorias
            equipe.derrotas = equipe.partidas_jogadas - equipe.vitorias
            equipe.pontuacao_total += pontos
            self.db.commit()
            self.db.refresh(equipe)
        return equipe