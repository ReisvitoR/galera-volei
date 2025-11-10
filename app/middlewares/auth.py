from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import security
from app.models import Usuario
from app.schemas import TokenData

# HTTP Bearer token scheme
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Middleware para autenticação - verifica token JWT e retorna usuário atual
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar token
        user_id = security.verify_token(credentials.credentials)
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=int(user_id))
    except Exception:
        raise credentials_exception
    
    # Buscar usuário no banco
    user = db.query(Usuario).filter(Usuario.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
        
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    return user


def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependência que garante que o usuário está ativo
    """
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuário inativo"
        )
    return current_user


def require_user_type(*allowed_types):
    """
    Decorator para autorização baseada em tipo de usuário
    """
    def decorator(current_user: Usuario = Depends(get_current_active_user)):
        if current_user.tipo not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta operação"
            )
        return current_user
    return decorator


def require_admin():
    """
    Dependência que requer usuário admin (profissional)
    """
    from app.models.enums import TipoUsuario
    return require_user_type(TipoUsuario.PROFISSIONAL)


def require_intermediate_or_above():
    """
    Dependência que requer usuário intermediário ou superior
    """
    from app.models.enums import TipoUsuario
    return require_user_type(
        TipoUsuario.INTERMEDIARIO, 
        TipoUsuario.AVANCADO,
        TipoUsuario.PROFISSIONAL
    )


def check_resource_owner(resource_user_id: int):
    """
    Middleware para verificar se o usuário é dono do recurso
    """
    def dependency(current_user: Usuario = Depends(get_current_active_user)):
        if current_user.id != resource_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você não tem permissão para acessar este recurso"
            )
        return current_user
    return dependency