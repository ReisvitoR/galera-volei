from typing import List
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import (
    UsuarioResponse, UsuarioUpdate, UsuarioRanking
)
from app.services import UsuarioService
from app.middlewares import get_current_active_user, require_admin
from app.models import Usuario
from app.models.enums import TipoUsuario

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar todos os usuários (paginado)
    """
    usuario_service = UsuarioService(db)
    return usuario_service.get_usuarios(skip=skip, limit=limit)


@router.get("/tipo/{tipo}", response_model=List[UsuarioResponse])
def listar_usuarios_por_tipo(
    tipo: TipoUsuario = Path(..., description="Tipo de usuário"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar usuários por tipo
    """
    usuario_service = UsuarioService(db)
    return usuario_service.get_usuarios_by_tipo(tipo, skip=skip, limit=limit)


@router.get("/ranking", response_model=List[UsuarioRanking])
def obter_ranking(
    limit: int = Query(10, ge=1, le=50, description="Limite de usuários no ranking"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obter ranking de usuários por pontuação
    """
    usuario_service = UsuarioService(db)
    return usuario_service.get_ranking(limit=limit)


@router.get("/melhores-atletas", response_model=List[UsuarioRanking])
def obter_melhores_atletas(
    limit: int = Query(10, ge=1, le=50, description="Limite de atletas"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obter melhores atletas por taxa de vitória
    """
    usuario_service = UsuarioService(db)
    return usuario_service.get_melhores_atletas(limit=limit)


@router.get("/{user_id}", response_model=UsuarioResponse)
def obter_usuario(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obter usuário por ID
    """
    usuario_service = UsuarioService(db)
    return usuario_service.get_usuario(user_id)


@router.put("/{user_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    user_id: int = Path(..., description="ID do usuário"),
    usuario_data: UsuarioUpdate = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Atualizar dados do usuário
    Usuário só pode alterar próprio perfil, exceto admins
    """
    usuario_service = UsuarioService(db)
    return usuario_service.update_usuario(user_id, usuario_data, current_user)


@router.delete("/{user_id}")
def desativar_usuario(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin())
):
    """
    Desativar usuário (apenas admins)
    """
    usuario_service = UsuarioService(db)
    usuario_service.deactivate_usuario(user_id, current_user)
    return {"message": "Usuário desativado com sucesso"}