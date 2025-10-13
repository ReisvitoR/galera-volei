from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Usuario
from app.models.enums import TipoUsuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """Repository para operações com usuários"""
    
    def __init__(self, db: Session):
        super().__init__(db, Usuario)
    
    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Buscar usuário por email"""
        return self.db.query(Usuario).filter(Usuario.email == email).first()
    
    def get_by_tipo(self, tipo: TipoUsuario, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Buscar usuários por tipo"""
        return (
            self.db.query(Usuario)
            .filter(Usuario.tipo == tipo)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_ranking(self, limit: int = 10) -> List[Usuario]:
        """Buscar ranking de usuários por pontuação"""
        return (
            self.db.query(Usuario)
            .filter(Usuario.ativo == True)
            .order_by(desc(Usuario.pontuacao_total))
            .limit(limit)
            .all()
        )
    
    def get_melhores_atletas(self, limit: int = 10) -> List[Usuario]:
        """Buscar melhores atletas por taxa de vitória"""
        return (
            self.db.query(Usuario)
            .filter(Usuario.ativo == True)
            .filter(Usuario.partidas_jogadas > 0)
            .order_by(desc(Usuario.vitorias / Usuario.partidas_jogadas))
            .limit(limit)
            .all()
        )
    
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar se email já existe"""
        query = self.db.query(Usuario).filter(Usuario.email == email)
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None
    
    def update_stats(self, user_id: int, partidas_jogadas: int = 1, vitorias: int = 0, pontos: int = 0):
        """Atualizar estatísticas do usuário"""
        user = self.get(user_id)
        if user:
            user.partidas_jogadas += partidas_jogadas
            user.vitorias += vitorias
            user.derrotas = user.partidas_jogadas - user.vitorias
            user.pontuacao_total += pontos
            self.db.commit()
            self.db.refresh(user)
        return user