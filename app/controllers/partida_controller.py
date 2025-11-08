from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import (
    PartidaCreate, PartidaUpdate, PartidaResponse, StatusResponse
)
from app.services import PartidaService
from app.middlewares import get_current_active_user, require_intermediate_or_above
from app.models import Usuario
from app.models.enums import TipoPartida, CategoriaPartida

router = APIRouter(prefix="/partidas", tags=["Partidas"])


@router.post("/", response_model=PartidaResponse, status_code=status.HTTP_201_CREATED)
def criar_partida(
    partida_data: PartidaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Criar nova partida
    """
    partida_service = PartidaService(db)
    return partida_service.create_partida(partida_data, current_user)


@router.get("/", response_model=List[PartidaResponse])
def listar_partidas_ativas(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    apenas_acessiveis: bool = Query(False, description="Mostrar apenas partidas que o usuário pode participar"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar partidas ativas com filtros opcionais por categoria
    """
    partida_service = PartidaService(db)
    return partida_service.get_partidas_ativas(
        skip=skip, 
        limit=limit, 
        categoria=categoria,
        usuario=current_user if apenas_acessiveis else None
    )


@router.get("/tipo/{tipo}", response_model=List[PartidaResponse])
def listar_partidas_por_tipo(
    tipo: TipoPartida = Path(..., description="Tipo de partida"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar partidas por tipo
    """
    partida_service = PartidaService(db)
    return partida_service.get_partidas_by_tipo(tipo, skip=skip, limit=limit)


@router.get("/proximas", response_model=List[PartidaResponse])
def listar_proximas_partidas(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar próximas partidas
    """
    partida_service = PartidaService(db)
    return partida_service.get_proximas_partidas(skip=skip, limit=limit)


@router.get("/minhas", response_model=List[PartidaResponse])
def listar_minhas_partidas(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar partidas organizadas pelo usuário logado
    """
    partida_service = PartidaService(db)
    return partida_service.get_minhas_partidas(current_user.id, skip=skip, limit=limit)


@router.get("/participando", response_model=List[PartidaResponse])
def listar_partidas_participando(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar partidas onde usuário está participando
    """
    partida_service = PartidaService(db)
    return partida_service.get_partidas_participando(current_user.id, skip=skip, limit=limit)


@router.get("/{partida_id}", response_model=PartidaResponse)
def obter_partida(
    partida_id: int = Path(..., description="ID da partida"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obter detalhes de uma partida
    """
    partida_service = PartidaService(db)
    return partida_service.get_partida(partida_id)


@router.put("/{partida_id}", response_model=PartidaResponse)
def atualizar_partida(
    partida_id: int = Path(..., description="ID da partida"),
    partida_data: PartidaUpdate = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Atualizar partida (apenas organizador)
    """
    partida_service = PartidaService(db)
    return partida_service.update_partida(partida_id, partida_data, current_user)


@router.patch("/{partida_id}/ativar", response_model=StatusResponse)
def ativar_partida(
    partida_id: int = Path(..., description="ID da partida"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Ativar partida (apenas organizador)
    """
    partida_service = PartidaService(db)
    partida_service.ativar_partida(partida_id, current_user)
    return StatusResponse(
        success=True,
        message="Partida ativada com sucesso"
    )


@router.patch("/{partida_id}/desativar", response_model=StatusResponse)
def desativar_partida(
    partida_id: int = Path(..., description="ID da partida"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Desativar partida (organizador ou admin)
    """
    partida_service = PartidaService(db)
    partida_service.desativar_partida(partida_id, current_user)
    return StatusResponse(
        success=True,
        message="Partida desativada com sucesso"
    )


@router.post("/{partida_id}/participar", response_model=PartidaResponse)
def participar_partida(
    partida_id: int = Path(..., description="ID da partida"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Participar de uma partida pública (com validação de categoria)
    """
    partida_service = PartidaService(db)
    return partida_service.participar_partida(partida_id, current_user)


@router.delete("/{partida_id}/participar", response_model=PartidaResponse)
def sair_partida(
    partida_id: int = Path(..., description="ID da partida"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Sair de uma partida
    """
    partida_service = PartidaService(db)
    return partida_service.sair_partida(partida_id, current_user)


@router.delete("/{partida_id}/participantes/{usuario_id}", response_model=PartidaResponse)
def remover_participante(
    partida_id: int = Path(..., description="ID da partida"),
    usuario_id: int = Path(..., description="ID do usuário a ser removido"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Remover um participante da partida (apenas organizador)
    """
    partida_service = PartidaService(db)
    return partida_service.remover_participante(partida_id, usuario_id, current_user)
    return partida_service.sair_partida(partida_id, current_user)


@router.patch("/{partida_id}/finalizar", response_model=PartidaResponse)
def finalizar_partida(
    partida_id: int = Path(..., description="ID da partida"),
    pontos_a: int = Query(..., ge=0, description="Pontuação da equipe A"),
    pontos_b: int = Query(..., ge=0, description="Pontuação da equipe B"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Finalizar partida com pontuação (apenas organizador)
    """
    partida_service = PartidaService(db)
    return partida_service.finalizar_partida(partida_id, pontos_a, pontos_b, current_user)