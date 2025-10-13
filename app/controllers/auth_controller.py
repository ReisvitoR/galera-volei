from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import Token, LoginRequest, UsuarioCreate, UsuarioResponse
from app.services import AuthService
from app.middlewares import get_current_active_user
from app.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar novo usuário
    """
    auth_service = AuthService(db)
    return auth_service.register(usuario_data)


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Fazer login e obter token de acesso
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Renovar token de acesso
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(current_user)


@router.get("/me", response_model=UsuarioResponse)
def get_current_user_info(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obter informações do usuário logado
    """
    return current_user