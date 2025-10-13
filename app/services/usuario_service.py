from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Usuario
from app.models.enums import TipoUsuario
from app.repositories import UsuarioRepository
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioRanking
from app.core.security import security


class UsuarioService:
    """
    Service para lógica de negócio dos usuários
    Implementa Single Responsibility Principle (SRP) do SOLID
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UsuarioRepository(db)
    
    def create_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """Criar novo usuário"""
        # Verificar se email já existe
        if self.repository.email_exists(usuario_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Hash da senha
        senha_hash = security.get_password_hash(usuario_data.senha)
        
        # Criar usuário
        usuario_dict = usuario_data.dict(exclude={'senha'})
        usuario_dict['senha_hash'] = senha_hash
        
        return self.repository.create(usuario_dict)
    
    def authenticate_usuario(self, email: str, senha: str) -> Optional[Usuario]:
        """Autenticar usuário"""
        usuario = self.repository.get_by_email(email)
        if not usuario:
            return None
        
        if not security.verify_password(senha, usuario.senha_hash):
            return None
        
        return usuario
    
    def get_usuario(self, user_id: int) -> Optional[Usuario]:
        """Buscar usuário por ID"""
        usuario = self.repository.get(user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return usuario
    
    def update_usuario(self, user_id: int, usuario_data: UsuarioUpdate, current_user: Usuario) -> Usuario:
        """Atualizar usuário"""
        # Verificar se usuário existe
        usuario = self.get_usuario(user_id)
        
        # Verificar permissão (só pode alterar próprio perfil ou ser admin)
        if current_user.id != user_id and current_user.tipo != TipoUsuario.PROPLAYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para alterar este usuário"
            )
        
        # Verificar se novo email já existe
        if usuario_data.email and self.repository.email_exists(usuario_data.email, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Atualizar apenas campos não nulos
        update_data = {k: v for k, v in usuario_data.dict().items() if v is not None}
        
        return self.repository.update(usuario, update_data)
    
    def get_usuarios(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Listar usuários"""
        return self.repository.get_multi(skip=skip, limit=limit)
    
    def get_usuarios_by_tipo(self, tipo: TipoUsuario, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Listar usuários por tipo"""
        return self.repository.get_by_tipo(tipo, skip=skip, limit=limit)
    
    def get_ranking(self, limit: int = 10) -> List[UsuarioRanking]:
        """Obter ranking de usuários"""
        usuarios = self.repository.get_ranking(limit=limit)
        
        ranking = []
        for usuario in usuarios:
            taxa_vitoria = (usuario.vitorias / usuario.partidas_jogadas * 100) if usuario.partidas_jogadas > 0 else 0
            ranking.append(UsuarioRanking(
                id=usuario.id,
                nome=usuario.nome,
                tipo=usuario.tipo,
                pontuacao_total=usuario.pontuacao_total,
                partidas_jogadas=usuario.partidas_jogadas,
                vitorias=usuario.vitorias,
                derrotas=usuario.derrotas,
                taxa_vitoria=round(taxa_vitoria, 2)
            ))
        
        return ranking
    
    def get_melhores_atletas(self, limit: int = 10) -> List[UsuarioRanking]:
        """Obter melhores atletas por taxa de vitória"""
        usuarios = self.repository.get_melhores_atletas(limit=limit)
        
        atletas = []
        for usuario in usuarios:
            taxa_vitoria = (usuario.vitorias / usuario.partidas_jogadas * 100) if usuario.partidas_jogadas > 0 else 0
            atletas.append(UsuarioRanking(
                id=usuario.id,
                nome=usuario.nome,
                tipo=usuario.tipo,
                pontuacao_total=usuario.pontuacao_total,
                partidas_jogadas=usuario.partidas_jogadas,
                vitorias=usuario.vitorias,
                derrotas=usuario.derrotas,
                taxa_vitoria=round(taxa_vitoria, 2)
            ))
        
        return atletas
    
    def deactivate_usuario(self, user_id: int, current_user: Usuario) -> Usuario:
        """Desativar usuário"""
        # Apenas admins podem desativar outros usuários
        if current_user.tipo != TipoUsuario.PROPLAYER and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para desativar este usuário"
            )
        
        usuario = self.get_usuario(user_id)
        return self.repository.update(usuario, {"ativo": False})