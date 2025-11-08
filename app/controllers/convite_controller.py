from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.convite_service import ConviteService
from app.schemas.schemas import ConviteCreate, ConviteUpdate, ConviteResponse
from app.middlewares.auth import get_current_user
from app.models.models import Usuario

router = APIRouter()


@router.post("/debug", status_code=status.HTTP_200_OK)
def debug_convite(
    convite: ConviteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint de debug para testar criação de convite
    """
    return {
        "message": "Debug endpoint funcionando",
        "convite_data": convite.model_dump(),
        "user_id": current_user.id,
        "db_connected": db is not None
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def enviar_convite(
    convite: ConviteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar um convite para um usuário participar de uma partida privada.
    Apenas o organizador da partida pode enviar convites.
    """
    try:
        print(f"DEBUG CONTROLLER: Recebendo convite: {convite}")
        print(f"DEBUG CONTROLLER: Usuario atual: {current_user.id}")
        
        convite_service = ConviteService(db)
        print(f"DEBUG CONTROLLER: Service criado")
        
        resultado = convite_service.enviar_convite(convite, current_user.id)
        print(f"DEBUG CONTROLLER: Resultado: {resultado}")
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG CONTROLLER: Erro capturado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put("/{convite_id}/aceitar", response_model=ConviteResponse)
def aceitar_convite(
    convite_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aceitar um convite recebido.
    Apenas o usuário convidado pode aceitar o convite.
    Ao aceitar, o usuário será automaticamente adicionado à partida.
    """
    try:
        convite_service = ConviteService(db)
        return convite_service.aceitar_convite(convite_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put("/{convite_id}/recusar", response_model=ConviteResponse)
def recusar_convite(
    convite_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recusar um convite recebido.
    Apenas o usuário convidado pode recusar o convite.
    """
    try:
        convite_service = ConviteService(db)
        return convite_service.recusar_convite(convite_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/enviados", response_model=List[ConviteResponse])
def get_convites_enviados(
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar todos os convites enviados pelo usuário atual.
    """
    convite_service = ConviteService(db)
    return convite_service.get_convites_enviados(current_user.id, skip, limit)


@router.get("/recebidos", response_model=List[ConviteResponse])
def get_convites_recebidos(
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar todos os convites recebidos pelo usuário atual.
    """
    convite_service = ConviteService(db)
    return convite_service.get_convites_recebidos(current_user.id, skip, limit)


@router.get("/{convite_id}", response_model=ConviteResponse)
def get_convite_by_id(
    convite_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar um convite específico por ID.
    Apenas usuários relacionados ao convite podem acessá-lo.
    """
    try:
        convite_service = ConviteService(db)
        convite = convite_service.get_convite_by_id(convite_id, current_user.id)
        if not convite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convite não encontrado"
            )
        return convite
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/pendentes", response_model=List[ConviteResponse])
def get_convites_pendentes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar todos os convites pendentes do usuário atual.
    """
    convite_service = ConviteService(db)
    return convite_service.get_convites_pendentes(current_user.id)


@router.get("/partida/{partida_id}", response_model=List[ConviteResponse])
def get_convites_da_partida(
    partida_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar todos os convites de uma partida específica.
    Apenas o organizador da partida pode ver estes convites.
    """
    convite_service = ConviteService(db)
    return convite_service.get_convites_da_partida(partida_id, current_user.id)


@router.delete("/{convite_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_convite(
    convite_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancelar um convite pendente.
    Apenas quem enviou o convite pode cancelá-lo.
    """
    convite_service = ConviteService(db)
    if not convite_service.cancelar_convite(convite_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convite não encontrado"
        )


@router.get("/{convite_id}", response_model=ConviteResponse)
def get_convite(
    convite_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar um convite específico por ID.
    Apenas o mandante ou o convidado podem ver o convite.
    """
    convite_service = ConviteService(db)
    convite = convite_service.convite_repo.get(convite_id)
    
    if not convite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convite não encontrado"
        )
    
    # Verificar se o usuário tem permissão para ver este convite
    if convite.mandante_id != current_user.id and convite.convidado_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para ver este convite"
        )
    
    return convite


@router.post("/expirar-antigos")
def expirar_convites_antigos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Expirar convites antigos (endpoint administrativo).
    Endpoint que pode ser usado para manutenção da base de dados.
    """
    convite_service = ConviteService(db)
    convites_expirados = convite_service.expirar_convites_antigos()
    return {"convites_expirados": convites_expirados}