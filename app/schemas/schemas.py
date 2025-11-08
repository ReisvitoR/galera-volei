from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.enums import TipoUsuario, TipoPartida, StatusPartida, StatusCandidatura, StatusConvite, CategoriaPartida

# ========== USUARIO SCHEMAS ==========
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    tipo: TipoUsuario = TipoUsuario.NOOB

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    tipo: Optional[TipoUsuario] = None
    ativo: Optional[bool] = None

class UsuarioInDB(UsuarioBase):
    id: int
    ativo: bool
    pontuacao_total: int
    partidas_jogadas: int
    vitorias: int
    derrotas: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioResponse(UsuarioInDB):
    pass

class UsuarioRanking(BaseModel):
    id: int
    nome: str
    tipo: TipoUsuario
    pontuacao_total: int
    partidas_jogadas: int
    vitorias: int
    derrotas: int
    taxa_vitoria: float
    
    model_config = ConfigDict(from_attributes=True)

# ========== PARTIDA SCHEMAS ==========
class PartidaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    tipo: TipoPartida
    categoria: str = "livre"
    data_partida: datetime
    local: Optional[str] = None
    max_participantes: int = 12
    publica: bool = True  # True = pública, False = privada

class PartidaCreate(PartidaBase):
    pass

class PartidaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[TipoPartida] = None
    categoria: Optional[str] = None
    data_partida: Optional[datetime] = None
    local: Optional[str] = None
    max_participantes: Optional[int] = None
    status: Optional[StatusPartida] = None
    pontuacao_equipe_a: Optional[int] = None
    pontuacao_equipe_b: Optional[int] = None

class PartidaInDB(PartidaBase):
    id: int
    status: StatusPartida
    pontuacao_equipe_a: int
    pontuacao_equipe_b: int
    organizador_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class PartidaResponse(PartidaInDB):
    organizador: UsuarioResponse
    participantes: List[UsuarioResponse] = []
    total_participantes: int = 0

# ========== EQUIPE SCHEMAS ==========
class EquipeBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class EquipeCreate(EquipeBase):
    pass

class EquipeUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None

class EquipeInDB(EquipeBase):
    id: int
    pontuacao_total: int
    partidas_jogadas: int
    vitorias: int
    derrotas: int
    lider_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class EquipeResponse(EquipeInDB):
    lider: UsuarioResponse
    membros: List[UsuarioResponse] = []
    taxa_vitoria: float = 0.0

# ========== CANDIDATURA SCHEMAS ==========
class CandidaturaBase(BaseModel):
    mensagem: Optional[str] = None

class CandidaturaCreate(CandidaturaBase):
    partida_id: int

class CandidaturaUpdate(BaseModel):
    status: StatusCandidatura
    mensagem: Optional[str] = None

class CandidaturaInDB(CandidaturaBase):
    id: int
    status: StatusCandidatura
    usuario_id: int
    partida_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class CandidaturaResponse(CandidaturaInDB):
    usuario: UsuarioResponse
    partida: PartidaResponse

# ========== AVALIACAO SCHEMAS ==========
class AvaliacaoBase(BaseModel):
    nota: int  # 1-5
    comentario: Optional[str] = None
    tipo_avaliacao: str  # "partida", "organizador", "jogador"

class AvaliacaoCreate(AvaliacaoBase):
    partida_id: int
    avaliado_id: Optional[int] = None  # null se for avaliação de partida

class AvaliacaoInDB(AvaliacaoBase):
    id: int
    avaliador_id: int
    avaliado_id: Optional[int]
    partida_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AvaliacaoResponse(AvaliacaoInDB):
    avaliador: UsuarioResponse
    avaliado: Optional[UsuarioResponse] = None
    partida: PartidaResponse

# ========== AUTH SCHEMAS ==========
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

# ========== CONVITE SCHEMAS ==========
class ConviteBase(BaseModel):
    mensagem: Optional[str] = None
    data_expiracao: Optional[datetime] = None

class ConviteCreate(ConviteBase):
    convidado_id: int
    partida_id: int

class ConviteUpdate(BaseModel):
    status: StatusConvite
    mensagem: Optional[str] = None

class ConviteInDB(ConviteBase):
    id: int
    status: StatusConvite
    mandante_id: int
    convidado_id: int
    partida_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class ConviteResponse(ConviteInDB):
    mandante: UsuarioResponse
    convidado: UsuarioResponse
    partida: PartidaResponse

# ========== RESPONSE SCHEMAS ==========
class StatusResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None