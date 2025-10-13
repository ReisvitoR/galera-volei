from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Usuario
from app.schemas import LoginRequest, Token, UsuarioCreate
from app.services.usuario_service import UsuarioService
from app.core.security import security


class AuthService:
    """
    Service para autenticação e autorização
    Implementa Single Responsibility Principle (SRP) do SOLID
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.usuario_service = UsuarioService(db)
    
    def register(self, usuario_data: UsuarioCreate) -> Token:
        """Registrar novo usuário"""
        # Criar usuário
        usuario = self.usuario_service.create_usuario(usuario_data)
        
        # Gerar token
        access_token = security.create_access_token(subject=usuario.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=usuario
        )
    
    def login(self, login_data: LoginRequest) -> Token:
        """Fazer login"""
        # Autenticar usuário
        usuario = self.usuario_service.authenticate_usuario(
            email=login_data.email,
            senha=login_data.senha
        )
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário inativo"
            )
        
        # Gerar token
        access_token = security.create_access_token(subject=usuario.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=usuario
        )
    
    def refresh_token(self, current_user: Usuario) -> Token:
        """Renovar token"""
        if not current_user.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário inativo"
            )
        
        access_token = security.create_access_token(subject=current_user.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=current_user
        )
    
    def verify_token(self, token: str) -> Optional[Usuario]:
        """Verificar token e retornar usuário"""
        user_id = security.verify_token(token)
        if not user_id:
            return None
            
        return self.usuario_service.get_usuario(int(user_id))